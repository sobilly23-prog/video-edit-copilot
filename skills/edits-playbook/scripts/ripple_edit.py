"""Mid-film picture edits in the open Edits project, with a report of everything Edits moved as a result.
  python3 -I ripple_edit.py "<project title>" insert <file> <before_clip_id> <srcIn> <srcOut> <volume>
  python3 -I ripple_edit.py "<project title>" extend <clip_id> <left_s> <right_s>     (seconds to ADD on each side)
  python3 -I ripple_edit.py "<project title>" els <t0> <t1>                          (list elements in a range)
<file> may be a path, or a name looked up in "work_media" from settings.json (copy source files there first; never
work on the originals). After every edit it prints each non-main element whose start/end changed: captions and
layers usually ripple, music never does, so re-fit with remap_layers.py afterwards."""
import sys, os, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard, elements, main_track, settings, src_in


def report(before, after, skip=()):
    out = []
    for i, a in after.items():
        b = before.get(i)
        if i in skip:
            continue
        if b is None:
            out.append(('NEW', a.get('content'), i[:8], round(a['startTime'], 3), round(a['endTime'], 3)))
        elif abs(a['startTime'] - b['startTime']) > 1e-3 or abs(a['endTime'] - b['endTime']) > 1e-3:
            out.append(('MOVED', a.get('content'), i[:8], round(b['startTime'], 3), round(b['endTime'], 3), '->',
                        round(a['startTime'], 3), round(a['endTime'], 3), (a.get('text') or a.get('title') or '')[:30]))
    out += [('GONE', before[i].get('content'), i[:8]) for i in before if i not in after]
    return out


def seek_frame(t):
    """Edits sometimes refuses a seek to an exact frame time; nudge and confirm the playhead landed."""
    for pre, d in ((None, 0), (None, 0.01), (round(t) - 2, 0.01), (round(t) + 2, 0.015), (None, 0.02)):
        try:
            if pre is not None:
                call('seek', seconds=pre); time.sleep(0.3)
            call('seek', seconds=t + d)
        except RuntimeError:
            time.sleep(0.3)
        if abs((call('state').get('currentTime') or 0) - t) < 0.02:
            return
    raise RuntimeError(f'could not put the playhead on {t:.3f}')


def insert(path, before_id, s_in, s_out, volume):
    """Insert a trimmed clip immediately BEFORE clip `before_id` on the main track (imports land at the playhead)."""
    els0 = elements()
    seek_frame(els0[before_id]['startTime'])
    eid = call('importMedia', path=path)['id']
    dur = call('getElement', id=eid)['duration']
    if s_in > 0.01:
        call('trim', id=eid, side='left', deltaSeconds=s_in)
    if dur - min(s_out, dur) > 0.02:
        call('trim', id=eid, side='right', deltaSeconds=dur - min(s_out, dur))
    call('setVolume', id=eid, volume=volume)
    ids = [e['id'] for e in main_track(elements())]
    if ids.index(eid) + 1 != ids.index(before_id):
        call('reorderClip', id=eid, position=ids.index(before_id) - (1 if ids.index(eid) < ids.index(before_id) else 0))
    els1 = elements()
    n = els1[eid]
    print(f"inserted {os.path.basename(path)} s{src_in(n):.3f}-{n.get('sourceOutPoint', 0):.3f} at "
          f"{n['startTime']:.3f}-{n['endTime']:.3f} vol {volume} (before {before_id[:8]}, now {els1[before_id]['startTime']:.3f})")
    return eid, els0, els1


def extend(cid, left, right):
    els0 = elements()
    if left:
        call('trim', id=cid, side='left', deltaSeconds=-left)      # negative = extend the in-point
    if right:
        call('trim', id=cid, side='right', deltaSeconds=-right)    # negative = extend the out-point
    els1 = elements()
    a, b = els0[cid], els1[cid]
    print(f"extended {cid[:8]}: @{a['startTime']:.3f}-{a['endTime']:.3f} -> @{b['startTime']:.3f}-{b['endTime']:.3f}")
    return els0, els1


def full_id(prefix):
    m = [i for i in elements() if i.startswith(prefix)]
    if len(m) != 1:
        sys.exit(f'{prefix!r} matches {len(m)} elements')
    return m[0]


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    title, cmd, *a = sys.argv[1:]
    guard(title)
    if cmd == 'insert':
        work = settings().get('work_media') or ''
        f = a[0] if os.path.exists(a[0]) else (glob.glob(os.path.join(work, f'*{a[0]}*')) or [a[0]])[0]
        eid, b, c = insert(f, full_id(a[1]), float(a[2]), float(a[3]), float(a[4]))
        for m in report(b, c, skip={eid}):
            print(' ', *m)
    elif cmd == 'extend':
        cid = full_id(a[0])
        b, c = extend(cid, float(a[1]), float(a[2]))
        for m in report(b, c, skip={cid}):
            print(' ', *m)
    elif cmd == 'els':
        t0, t1 = float(a[0]), float(a[1])
        for e in sorted(elements().values(), key=lambda e: (e['startTime'], e.get('content') or '')):
            if e['endTime'] > t0 and e['startTime'] < t1:
                print(e['id'], e.get('content'), round(e['startTime'], 3), round(e['endTime'], 3),
                      (e.get('text') or e.get('title') or e.get('effectDisplayName') or '')[:40])
    print('duration', call('state').get('duration'))
