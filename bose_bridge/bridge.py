#!/usr/bin/env python3
"""
Bose SoundTouch preset-to-radio bridge.

Listens to the speaker's WebSocket notification stream. When a preset
button is pressed, pushes the configured stream URL via UPnP
SetAVTransportURI + Play.

Works around the firmware bug where UPNP-source presets save but never
play back on recall. Also restores radio playback after the Bose cloud
retirement broke TuneIn / LOCAL_INTERNET_RADIO presets.
"""

import json
import os
import re
import socket
import time
import urllib.request
import xml.etree.ElementTree as ET

import upnpclient
import websocket

OPTIONS_PATH = "/data/options.json"
PRESET_RE = re.compile(r'<nowSelectionUpdated>\s*<preset id="(\d+)"')
SSDP_ADDR = ("239.255.255.250", 1900)
SSDP_TARGET = "urn:schemas-upnp-org:device:MediaRenderer:1"


def load_options() -> dict:
    if not os.path.exists(OPTIONS_PATH):
        print(f"[cfg] {OPTIONS_PATH} missing — running with empty config")
        return {}
    with open(OPTIONS_PATH) as f:
        return json.load(f)


def discover_soundtouch() -> str | None:
    """Return the IP of the first Bose SoundTouch found via SSDP, or None."""
    msg = (
        "M-SEARCH * HTTP/1.1\r\n"
        f"HOST: {SSDP_ADDR[0]}:{SSDP_ADDR[1]}\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 2\r\n"
        f"ST: {SSDP_TARGET}\r\n\r\n"
    ).encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    s.sendto(msg, SSDP_ADDR)
    try:
        while True:
            data, addr = s.recvfrom(2048)
            text = data.decode(errors="ignore")
            loc = next(
                (l.split(": ", 1)[1].strip() for l in text.split("\r\n") if l.lower().startswith("location:")),
                None,
            )
            if not loc:
                continue
            try:
                desc = urllib.request.urlopen(loc, timeout=3).read().decode()
            except Exception:
                continue
            if "SoundTouch" in desc or "Bose" in desc:
                return addr[0]
    except socket.timeout:
        return None
    finally:
        s.close()


def device_url_for(host: str) -> str:
    """Fetch /info on the speaker and build the UPnP description URL."""
    with urllib.request.urlopen(f"http://{host}:8090/info", timeout=5) as r:
        info_xml = r.read().decode()
    m = re.search(r'deviceID="([0-9A-F]+)"', info_xml)
    if not m:
        raise RuntimeError(f"could not parse deviceID from http://{host}:8090/info")
    return f"http://{host}:8091/XD/BO5EBO5E-F00D-F00D-FEED-{m.group(1)}.xml"


def get_av_service(host: str):
    desc_url = device_url_for(host)
    print(f"[upnp] description: {desc_url}")
    d = upnpclient.Device(desc_url)
    return next(s for s in d.services if "AVTransport" in s.service_id)


def play(av, url: str):
    av.SetAVTransportURI(InstanceID=0, CurrentURI=url, CurrentURIMetaData="")
    av.Play(InstanceID=0, Speed="1")


def main():
    cfg = load_options()
    host = (cfg.get("bose_host") or "").strip()
    if not host:
        print("[cfg] bose_host blank — auto-discovering via SSDP...")
        host = discover_soundtouch()
        if not host:
            raise SystemExit(
                "no SoundTouch found on the network. Set bose_host in the addon "
                "Configuration tab and restart."
            )
        print(f"[cfg] discovered SoundTouch at {host}")

    presets = {i: (cfg.get(f"preset_{i}_url") or "").strip() for i in range(1, 7)}

    print("[cfg] preset map:")
    for i, url in presets.items():
        print(f"  {i}: {url or '(unset — preset will be ignored)'}")

    av = get_av_service(host)

    def on_message(ws, msg):
        m = PRESET_RE.search(msg)
        if not m:
            return
        pid = int(m.group(1))
        if pid == 0:
            return
        url = presets.get(pid, "")
        if not url:
            print(f"[ws] preset {pid} pressed (no URL configured)")
            return
        print(f"[ws] preset {pid} pressed -> {url}")
        try:
            play(av, url)
            print("[ws] playing")
        except Exception as e:
            print(f"[ws] play failed: {e}")

    def on_open(ws):
        print(f"[ws] connected to ws://{host}:8080")

    def on_error(ws, e):
        print(f"[ws] error: {e}")

    def on_close(ws, code, reason):
        print(f"[ws] closed: {code} {reason}")

    while True:
        ws = websocket.WebSocketApp(
            f"ws://{host}:8080",
            subprotocols=["gabbo"],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever(ping_interval=30, ping_timeout=10)
        print("[ws] reconnecting in 5s")
        time.sleep(5)


if __name__ == "__main__":
    main()
