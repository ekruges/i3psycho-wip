# Changelog

## v0.1.0 (2026-07-27)

First tagged release. Everything below is verified by the phase test
suites (test/phase0-4.sh) and by upstream i3's complete test suite
(284 files, 4190 tests, PASS) running against the patched binary.

### Fork (4 patches on i3 master f7d5b898, patches/)
- window::move IPC events for floating repositions (0001, upstreamable)
- Titlebar buttons on floating windows: close / iconify / maximize,
  bare glyphs in the titlebar text color; double-click titlebar
  fullscreen (0002)
- Live edge-snap preview and exact snap-on-drop in the drag loop (0003)
- App iconify honored (WM_CHANGE_STATE): in-app minimize buttons work;
  scratchpad windows expose _NET_WM_STATE_HIDDEN + WM_STATE Iconic (0004)

### psychod
- Cascade placement, exact workarea snapping, minimize with geometry
  restore (including retroactive save for any scratchpad arrival),
  drop-snap polling for stock i3, MRU cycling, expose grid, show
  desktop, hot corners
- Survives i3 restarts (connection rebuild), one instance per display,
  every action guarded; a failing action logs instead of killing the daemon
- psychod-status: bar statusline wrapper with clickable minimized-window
  chips; accepts JSON and plain-text status sources

### Distribution
- PKGBUILD (provides/conflicts i3-wm, the i3-gaps model), xsession entry,
  session launcher that respects an existing user config
- include-able dist/psycho.conf for existing i3 configs; standalone
  psycho.config for fresh installs
- USERGUIDE.md (with the complete list of behavior deviations from
  stock i3), psychod.1 man page, invisible vsync-only picom.conf
