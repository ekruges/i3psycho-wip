#!/usr/bin/env python3
"""psychod — i3psycho Phase 1 companion daemon.

Cascade placement, exact-workarea snapping, geometry-remembering minimize,
drag-beyond-edge snapping, MRU toggle, show-desktop. Pure i3 IPC, no X calls.

Triggers: `bindsym ... nop psycho:<action>` in the i3 config (binding events)
or `i3-msg -t send_tick psycho:<action>` from scripts. Actions:
  snap:left|right|max|center|tl|tr|bl|br   minimize (min) / restore[:conid]
  mru / showdesktop
"""
import argparse
import collections
import threading
import time

from i3ipc import Connection, Event

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--cascade-step", type=int, default=30)
ap.add_argument("--edge-margin", type=int, default=25,
                help="px beyond the workarea edge that triggers drop-snap")
ap.add_argument("--drop-debounce", type=float, default=0.4)
ARGS = ap.parse_args()

conn = Connection()
mru = collections.deque(maxlen=64)          # focus history, most recent last
saved = {}                                  # con_id -> (x, y, w, h) container rect
min_stack = []                              # LIFO of minimized con_ids
desktop_stash = collections.defaultdict(list)  # ws name -> [con_ids]
cascade_n = collections.defaultdict(int)    # ws name -> spawn counter
cascaded = set()
suppress = {}                               # con_id -> ignore moves until (monotonic)


def floating_parent(con):
    if con is None:
        return None
    if con.type == "floating_con":
        return con
    if con.parent is not None and con.parent.type == "floating_con":
        return con.parent
    return None


def scratch_leaves(tree):
    sp = tree.scratchpad()
    return [leaf for f in sp.floating_nodes for leaf in f.leaves()]


def workarea(con):
    ws = con.workspace()
    return ws.rect if ws else None


def place(c, con, x, y, w, h):
    """Move/size a floating container so its OUTER rect is exactly x,y,w,h.
    Since i3 4.21, `resize set ... px` on floating containers includes the
    decorations, so no chrome math is needed."""
    suppress[con.id] = time.monotonic() + 0.5
    c.command(f'[con_id="{con.id}"] resize set {int(w)} px {int(h)} px, '
              f'move absolute position {int(x)} px {int(y)} px')


def region_rect(wa, region):
    x, y, w, h = wa.x, wa.y, wa.width, wa.height
    return {
        "left":   (x, y, w // 2, h),
        "right":  (x + w // 2, y, w - w // 2, h),
        "max":    (x, y, w, h),
        "center": (x + int(w * 0.19), y + int(h * 0.19), int(w * 0.62), int(h * 0.62)),
        "tl":     (x, y, w // 2, h // 2),
        "tr":     (x + w // 2, y, w - w // 2, h // 2),
        "bl":     (x, y + h // 2, w // 2, h - h // 2),
        "br":     (x + w // 2, y + h // 2, w - w // 2, h - h // 2),
    }.get(region)


def focused_float(c):
    tree = c.get_tree()
    f = tree.find_focused()
    if f is None or f.workspace() is None or f.workspace().name.startswith("__"):
        return None
    if floating_parent(f) is None:
        c.command(f'[con_id="{f.id}"] floating enable')
        f = c.get_tree().find_by_id(f.id)
    return f


def do_snap(region):
    f = focused_float(conn)
    if f is None:
        return
    wa = workarea(f)
    r = region_rect(wa, region) if wa else None
    if r:
        place(conn, f, *r)


def do_minimize():
    f = focused_float(conn)
    if f is None:
        return
    fc = floating_parent(f)
    saved[f.id] = (fc.rect.x, fc.rect.y, fc.rect.width, fc.rect.height)
    min_stack.append(f.id)
    conn.command(f'[con_id="{f.id}"] move scratchpad')


def do_restore(cid=None):
    if cid is None:
        cid = min_stack.pop() if min_stack else None
    else:
        cid = int(cid)
        if cid in min_stack:
            min_stack.remove(cid)
    if cid is None:
        return
    conn.command(f'[con_id="{cid}"] scratchpad show')
    con = conn.get_tree().find_by_id(cid)
    if con is not None and cid in saved:
        place(conn, con, *saved.pop(cid))


def do_mru():
    tree = conn.get_tree()
    seen = set()
    order = []
    for cid in reversed(mru):
        if cid not in seen and tree.find_by_id(cid) is not None:
            seen.add(cid)
            order.append(cid)
    if len(order) >= 2:
        conn.command(f'[con_id="{order[1]}"] focus')


def do_showdesktop():
    tree = conn.get_tree()
    f = tree.find_focused()
    ws = f.workspace() if f else None
    if ws is None:
        return
    if desktop_stash[ws.name]:
        for cid in desktop_stash.pop(ws.name):
            do_restore(cid)
        return
    for fc in ws.floating_nodes:
        for leaf in fc.leaves():
            saved[leaf.id] = (fc.rect.x, fc.rect.y, fc.rect.width, fc.rect.height)
            desktop_stash[ws.name].append(leaf.id)
            conn.command(f'[con_id="{leaf.id}"] move scratchpad')


def dispatch(payload):
    if not payload.startswith("psycho:"):
        return
    parts = payload.split(":")
    action = parts[1]
    if action == "snap" and len(parts) > 2:
        do_snap(parts[2])
    elif action == "min":
        do_minimize()
    elif action == "restore":
        do_restore(parts[2] if len(parts) > 2 else None)
    elif action == "mru":
        do_mru()
    elif action == "showdesktop":
        do_showdesktop()


def cascade(con):
    if con.id in cascaded:
        return
    tree = conn.get_tree()
    c = tree.find_by_id(con.id)
    if c is None or floating_parent(c) is None:
        return
    wtype = getattr(c, "window_type", None)
    if wtype in ("dialog", "utility", "splash", "notification", "dock"):
        return
    ws = c.workspace()
    if ws is None or ws.name.startswith("__"):
        return
    if len(cascaded) > 512:
        cascaded.clear()
    cascaded.add(con.id)
    n = cascade_n[ws.name] % 8
    cascade_n[ws.name] += 1
    step = ARGS.cascade_step
    fc = floating_parent(c)
    x = ws.rect.x + 40 + n * step
    y = ws.rect.y + 36 + n * step
    x = min(x, ws.rect.x + ws.rect.width - fc.rect.width - 8)
    y = min(y, ws.rect.y + ws.rect.height - fc.rect.height - 8)
    suppress[con.id] = time.monotonic() + 0.5
    conn.command(f'[con_id="{con.id}"] move absolute position {int(x)} px {int(y)} px')


def on_new(_, e):
    cascade(e.container)


def on_floating(_, e):
    if e.change == "floating_on" or getattr(e.container, "floating", "") in ("auto_on", "user_on"):
        cascade(e.container)


def on_focus(_, e):
    mru.append(e.container.id)


def on_close(_, e):
    saved.pop(e.container.id, None)
    if e.container.id in min_stack:
        min_stack.remove(e.container.id)
    tree = conn.get_tree()
    for ws in tree.workspaces():
        if ws.name in cascade_n and not ws.floating_nodes:
            cascade_n[ws.name] = 0


def on_binding(_, e):
    cmd = (e.binding.command or "").strip()
    if cmd.startswith("nop "):
        dispatch(cmd[4:].strip())


def on_tick(_, e):
    if getattr(e, "first", False):
        return
    dispatch(e.payload or "")


def drop_worker():
    """Poll floating rects; when one settles beyond a workarea edge, snap it.
    ponytail: polling, because stock i3 emits no window::move events for
    floating repositions (verified empirically). The Phase 2 fork adds real
    drag events and a live preview; until then a 0.3s poll is invisible."""
    wconn = Connection()
    prev = {}      # leaf id -> outer rect tuple
    moving = {}    # leaf id -> last time the rect changed
    while True:
        time.sleep(0.3)
        try:
            tree = wconn.get_tree()
        except Exception:
            continue                      # i3 restarting
        now = time.monotonic()
        seen = set()
        for ws in tree.workspaces():
            if ws.name.startswith("__"):
                continue
            for fc in ws.floating_nodes:
                leaf = next(iter(fc.leaves()), None)
                if leaf is None:
                    continue
                cid = leaf.id
                seen.add(cid)
                pos = (fc.rect.x, fc.rect.y, fc.rect.width, fc.rect.height)
                if prev.get(cid) != pos:
                    prev[cid] = pos
                    if suppress.get(cid, 0) > now:
                        moving.pop(cid, None)     # our own placement
                    else:
                        moving[cid] = now
                elif cid in moving and now - moving[cid] >= ARGS.drop_debounce:
                    moving.pop(cid)
                    evaluate_drop(wconn, fc, leaf, ws.rect)
        for cid in [c for c in prev if c not in seen]:
            prev.pop(cid)
            moving.pop(cid, None)


def evaluate_drop(wconn, fc, leaf, wa):
    m = ARGS.edge_margin
    left = fc.rect.x < wa.x - m
    right = fc.rect.x + fc.rect.width > wa.x + wa.width + m
    top = fc.rect.y < wa.y - m
    bottom = fc.rect.y + fc.rect.height > wa.y + wa.height + m
    region = None
    if top and left:
        region = "tl"
    elif top and right:
        region = "tr"
    elif bottom and left:
        region = "bl"
    elif bottom and right:
        region = "br"
    elif top:
        region = "max"
    elif left:
        region = "left"
    elif right:
        region = "right"
    if region:
        place(wconn, leaf, *region_rect(wa, region))


def main():
    threading.Thread(target=drop_worker, daemon=True).start()
    conn.on(Event.WINDOW_NEW, on_new)
    conn.on(Event.WINDOW_FLOATING, on_floating)
    conn.on(Event.WINDOW_FOCUS, on_focus)
    conn.on(Event.WINDOW_CLOSE, on_close)
    conn.on(Event.BINDING, on_binding)
    conn.on(Event.TICK, on_tick)
    conn.main()


if __name__ == "__main__":
    main()
