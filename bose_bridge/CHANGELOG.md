# Changelog

## 1.2.1

- Fix multi-architecture build. The `1.2.0` Dockerfile only pulled the
  amd64 base image and failed on aarch64 (ARM64) Home Assistant
  installations. Re-added `build.yaml` mapping each supported
  architecture to its correct base image.
- Dropped deprecated `armv7`, `armhf`, `i386` from `arch` (modern
  Supervisor flags these). Supported architectures are now `amd64` and
  `aarch64`.

## 1.2.0

- Polished release for public use.
- Auto-discovers the SoundTouch via SSDP if `bose_host` is left blank.
- Auto-derives the UPnP description URL from the speaker's `/info`
  endpoint — works on any SoundTouch model out of the box.
- Removed deprecated `build.yaml` (FROM image inlined into Dockerfile).
- Default config is now empty so first-time users can paste their own
  URLs.

## 1.1.0

- Added 6 configurable preset URL fields and a `bose_host` field via the
  add-on **Configuration** tab.

## 1.0.0

- Initial WebSocket → UPnP bridge with hardcoded URL map.
