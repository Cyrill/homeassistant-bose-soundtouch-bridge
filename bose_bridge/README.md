# Bose SoundTouch Bridge

Brings the **physical preset buttons** on Bose SoundTouch speakers back
to life after the **Bose cloud retirement (2026)**.

## What this fixes

When the Bose cloud was retired, every preset that relied on it stopped
working — TuneIn presets, the SoundTouch app, and the
`LOCAL_INTERNET_RADIO` source all return errors. Spotify and AUX still
work, but the six physical buttons on top of the speaker are mostly dead.

This add-on revives them. It listens to the speaker's local WebSocket
notification stream and, whenever you press a preset button, pushes the
URL you configured for that slot via UPnP — using the local
`SetAVTransportURI` / `Play` calls that are still fully functional in
the firmware.

## What you get

- Press preset 1 → plays whatever stream URL you put in slot 1
- Press preset 2 → slot 2
- … and so on, all six buttons
- Configurable per-preset URLs in the add-on's **Configuration** tab
- Works with any plain HTTP/MP3 internet-radio stream (icecast, etc.)
- No Bose cloud, no app, no rooting — pure local network

## Requirements

- A Bose SoundTouch speaker (any model with the SoundTouch firmware) on
  the same network as Home Assistant
- Home Assistant OS or Supervised (the add-on runs as a Docker container
  managed by the Supervisor)

## Setup

1. Install this add-on (see *Install* below).
2. Open the add-on → **Configuration**.
3. Either leave `bose_host` blank to auto-discover the speaker via SSDP,
   or set it to the speaker's IP address (e.g. `192.168.1.42`).
4. Fill in `preset_1_url` … `preset_6_url` with the stream URLs you want
   each preset button to play. Leave any unused slots blank.
5. **Save** → **Start** → check the **Log** tab; it should print
   ```
   [cfg] preset map: ...
   [upnp] description: http://...
   [ws] connected to ws://...:8080
   ```

Press a preset button on the speaker and the radio should kick in.

## Example URLs (Belgian / Flemish radio)

| Preset | Station | URL |
|---|---|---|
| 1 | VRT Radio 1 | `http://icecast.vrtcdn.be/radio1-high.mp3` |
| 2 | VRT Radio 2 OVL | `http://icecast.vrtcdn.be/ra2ovl-high.mp3` |
| 3 | VRT Radio 1 Classics | `http://icecast.vrtcdn.be/radio1_classics-high.mp3` |
| 4 | VRT Studio Brussel | `http://icecast.vrtcdn.be/stubru-high.mp3` |
| 6 | VRT Nieuwsbrief | `http://progressive-audio.vrtcdn.be/content/fixed/11_11niws-snip_hi.mp3` |

For other stations, look up the direct stream URL on the broadcaster's
website (search for `icecast`, `mp3`, or `aac`). Some commercial stations
hide their URL behind authenticated tokens — those won't work without an
extra proxy and are out of scope for this add-on.

## Install

1. In Home Assistant: **Settings → Add-ons → App Store → ⋮ → Repositories**
2. Add this repository's GitHub URL
3. The "Bose SoundTouch Bridge" add-on appears in the store — click
   **Install** → **Start**

## How it works

- Bose's stock firmware exposes a WebSocket notification stream on
  `ws://<speaker>:8080` (subprotocol `gabbo`). It emits an event for
  every preset button press:
  `<nowSelectionUpdated><preset id="N">…`
- The same firmware exposes a UPnP `MediaRenderer` on port 8091 with a
  fully working `AVTransport` service (the very same one the SoundTouch
  app uses for "play this URL").
- The add-on stitches them together: catch the button event, push the
  URL via UPnP. No cloud needed.

## Limitations

- Only **plain HTTP audio streams** (no token-protected commercial
  streams without an extra proxy)
- The speaker's display still shows whatever the original preset is set
  to — buttons trigger the bridge regardless. If you want the right name
  to show up, store any UPnP placeholder as the preset on the speaker.
- One bridge per speaker. Multi-speaker support is on the roadmap.

## License

MIT
