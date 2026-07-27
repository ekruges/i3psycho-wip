<img src="logo-transparent.png" alt="i3psycho" width="720">

# i3psycho (wip)

i3 for psychopaths: floating-first i3, macOS-grade window behavior, the blue titlebar kept sacred.

The plan is canonical and lives in [i3psycho-plan](https://github.com/ekruges/i3psycho-plan).

## Status: Phase 1 shipped

`psychod` (Python, i3ipc, apt-installable deps only) now does the macOS part:
cascade placement of new windows, exact-workarea snapping (keyboard binds and
drag-beyond-edge), minimize with geometry restore, show desktop, MRU alt-tab,
and a minimized-window dock in the bar (`psychod-status` statusline wrapper,
click a chip to restore). `test/phase1.sh` verifies all of it headless under
Xvfb; `test/phase0.sh` still covers the config-only layer.

Known behavior:
- Terminals with size-hint increments (xterm) snap to the nearest character
  cell, so sub-cell gaps are normal - same as every WM, macOS included.
- Drop-snap is a 0.3s rect poll: stock i3 emits no `window::move` IPC events
  for floating repositions (verified empirically). The Phase 2 fork adds real
  drag events and a live snap preview.
- Multi-monitor is untested so far (single-screen Xvfb rig).

Phase 2 next: the fork - titlebar buttons, true minimize, drag events.

Layout (will grow per the plan):

```
i3/          # patched i3 fork, branch `psycho`, rebased on upstream tags
psychod/     # companion IPC daemon (Python, i3ipc)
dist/        # default config, picom.conf, skippy-xd.conf, rofi theme
packaging/   # PKGBUILD and friends
```
