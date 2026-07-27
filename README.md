<img src="logo-transparent.png" alt="i3psycho" width="720">

# i3psycho (wip)

i3 for psychopaths: floating-first i3, macOS-grade window behavior, the blue titlebar kept sacred. Nothing works yet.

The plan is canonical and lives in [i3psycho-plan](https://github.com/ekruges/i3psycho-plan).

## Status: Phase 0 shipped

`dist/psycho.config` runs on a bone-stock i3: float-by-default (`for_window [tiling]`), blue titlebars, keyboard snapping (halves / maximize / center / quarters), scratchpad-as-minimize. `test/phase0.sh` smoke-tests it headless under Xvfb and drops screenshots in /tmp.

Known limitations, all Phase 1 (psychod) work:
- Snap geometry is ppt of the full output: snapped windows overlap the bar, and bottom snaps overflow by the titlebar height. psychod will compute exact workarea rects.
- New windows spawn dead center, exactly stacked. Cascade placement is psychod's job.
- No drag-to-edge snapping yet (needs psychod watching move events).

Layout (will grow per the plan):

```
i3/          # patched i3 fork, branch `psycho`, rebased on upstream tags
psychod/     # companion IPC daemon (Python, i3ipc)
dist/        # default config, picom.conf, skippy-xd.conf, rofi theme
packaging/   # PKGBUILD and friends
```
