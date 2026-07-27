<img src="logo-transparent.png" alt="i3psycho" width="720">

# i3psycho (wip)

i3 for psychopaths: floating-first i3, macOS-grade window behavior, the blue titlebar kept sacred. Nothing works yet.

The plan is canonical and lives in [i3psycho-plan](https://github.com/ekruges/i3psycho-plan). Current phase: **Phase 0** (config-only prototype on stock i3 + picom + skippy-xd).

Layout (will grow per the plan):

```
i3/          # patched i3 fork, branch `psycho`, rebased on upstream tags
psychod/     # companion IPC daemon (Python, i3ipc)
dist/        # default config, picom.conf, skippy-xd.conf, rofi theme
packaging/   # PKGBUILD and friends
```
