<img src="logo-transparent.png" alt="i3psycho" width="720">

# i3psycho (wip)

i3 for psychopaths: floating-first i3, macOS-grade window behavior, the blue titlebar kept sacred.

The plan is canonical and lives in [i3psycho-plan](https://github.com/ekruges/i3psycho-plan).

## Status: Phase 2 shipped (the fork exists)

`psychod` (Python, i3ipc, apt-installable deps only) now does the macOS part:
cascade placement of new windows, exact-workarea snapping (keyboard binds and
drag-beyond-edge), minimize with geometry restore, show desktop, MRU alt-tab,
and a minimized-window dock in the bar (`psychod-status` statusline wrapper,
click a chip to restore). `test/phase1.sh` verifies all of it headless under
Xvfb; `test/phase0.sh` still covers the config-only layer.

Phase 2 adds the C patches (see `patches/`), built and verified on the CT:
- **Titlebar buttons** on floating windows: x (close), − (iconify to
  scratchpad), + (fullscreen). Minimal glyphs in the titlebar text color,
  macOS placement, themed by existing `client.*` directives. `deco_buttons.c`
  module, hit-tested in `route_click()` before drag/resize.
- **Double-click titlebar** toggles fullscreen (classic floating-WM behavior).
- **`window::move` IPC events for floating repositions** - upstreamable fix;
  psychod's poller keeps working on stock i3 either way, and retro-saves
  geometry for ANY scratchpad iconification (button, bind, or tick).

`test/phase2.sh` drives the buttons with xdotool clicks and verifies all of
it headless. `packaging/build-i3psycho.sh` builds upstream + patches.

Known behavior:
- Terminals with size-hint increments (xterm) snap to the nearest character
  cell, so sub-cell gaps are normal - same as every WM, macOS included.
- On stock i3, drop-snap relies on the 0.3s rect poll (no move events there).
  On the patched i3, moves emit events; the poller works for both.
- Multi-monitor is untested so far (single-screen Xvfb rig).

Phase 3 next: live snap preview in the drag loop, true `_NET_WM_STATE_HIDDEN` minimize, picom/skippy-xd dist configs, PKGBUILD for the AUR.

Layout (will grow per the plan):

```
i3/          # patched i3 fork, branch `psycho`, rebased on upstream tags
psychod/     # companion IPC daemon (Python, i3ipc)
dist/        # default config, picom.conf, skippy-xd.conf, rofi theme
packaging/   # PKGBUILD and friends
```
