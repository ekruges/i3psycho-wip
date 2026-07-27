# i3psycho fork patches

Applied on top of upstream i3 master (branch `psycho` on the build box is the
same series as commits). Regenerate with `git format-patch` after a rebase.

- `0001` — ipc: emit `window::move` for floating repositions. Upstreamable on
  its own; without it, IPC consumers must poll floating geometry.
- `0002` — decorations: titlebar buttons (close / iconify / maximize, minimal
  glyphs in the titlebar text color, macOS placement) + double-click-titlebar
  fullscreen. New `src/deco_buttons.c` module, wired into `x_draw_decoration()`
  and `route_click()`.
- `0003` — floating: live edge-snap preview in the drag loop (solid rect in
  the focused titlebar color, stacked under the dragged window) and exact
  snap-on-drop for halves / maximize / quarters. Zero per-motion work when
  the edge region is unchanged.
- `0004` — scratchpad: app iconify requests honored; hidden windows carry
  _NET_WM_STATE_HIDDEN and WM_STATE Iconic.
- `0005` — ipc/i3bar: GET_SCRATCHPAD (type 13) and native taskbar chips
  next to the workspace buttons (app icons, urgency blink, click restores).
- `0006` — scratchpad: the retro outline-box genie on minimize/restore.
- `0007` — config: the psycho_* directives (genie duration, buttons,
  double-click, snap edges/margin, chips).

Build:

```
git clone https://github.com/i3/i3 && cd i3
git am ../patches/00*.patch
meson setup --buildtype=release build && ninja -C build
```
