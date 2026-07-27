# i3psycho fork patches

Applied on top of upstream i3 master (branch `psycho` on the build box is the
same series as commits). Regenerate with `git format-patch` after a rebase.

- `0001` — ipc: emit `window::move` for floating repositions. Upstreamable on
  its own; without it, IPC consumers must poll floating geometry.
- `0002` — decorations: titlebar buttons (close / iconify / maximize, minimal
  glyphs in the titlebar text color, macOS placement) + double-click-titlebar
  fullscreen. New `src/deco_buttons.c` module, wired into `x_draw_decoration()`
  and `route_click()`.

Build:

```
git clone https://github.com/i3/i3 && cd i3
git am ../patches/00*.patch
meson setup build && ninja -C build
```
