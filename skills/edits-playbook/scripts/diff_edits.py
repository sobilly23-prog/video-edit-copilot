"""READ-ONLY: what changed between the copilot's hand-over and the user's review.
  python3 -I diff_edits.py <before.json> [--after <after.json>] [--from t0] [--to t1]
Without --after it compares against the live project. Lists main-track clips trimmed / extended / slipped / moved /
removed / added (with file names if video-edit-copilot/clipmap.json exists), then captions, music and adjustment
layers whose timing, volume or wording changed. Never edits anything. Feed the output to the learn skill."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import main_track, src_in

a = sys.argv[1:]
if not a:
    sys.exit(__doc__)
before = json.load(open(a[0]))
if '--after' in a:
    after_els = {e['id']: e for e in json.load(open(a[a.index('--after') + 1]))['elements']}
else:
    from edits_api import elements
    after_els = elements()
t0 = float(a[a.index('--from') + 1]) if '--from' in a else -1
t1 = float(a[a.index('--to') + 1]) if '--to' in a else 1e9
cmap_p = os.path.join(os.getcwd(), 'video-edit-copilot', 'clipmap.json')
cmap = json.load(open(cmap_p)) if os.path.exists(cmap_p) else {}
old = {e['id']: e for e in before['elements']}


def name(i):
    n = (cmap.get(i) or {}).get('name')
    return f'{n} ({i[:8]})' if n else i[:8]


def inside(e):
    return t0 <= e['startTime'] < t1


om, lm = main_track(old), main_track(after_els)
oid, lid = {e['id'] for e in om}, {e['id'] for e in lm}
print('MAIN TRACK  (start before -> after | length before -> after | source window | volume)')
for e in lm:
    o = old.get(e['id'])
    if not inside(e) and not (o and inside(o)):
        continue
    si, so = src_in(e), e.get('sourceOutPoint', 0) or 0
    if not o:
        print(f"  ADDED   {name(e['id']):24} @{e['startTime']:8.2f} len {e['endTime'] - e['startTime']:5.2f} src {si:.2f}-{so:.2f}")
        continue
    ol, nl = o['endTime'] - o['startTime'], e['endTime'] - e['startTime']
    osi, oso = src_in(o), o.get('sourceOutPoint', 0) or 0
    if abs(ol - nl) > 0.02 or abs(osi - si) > 0.02 or abs((e.get('volume') or 0) - (o.get('volume') or 0)) > 0.005:
        print(f"  {name(e['id']):24} @{o['startTime']:8.2f}->{e['startTime']:8.2f} | {ol:5.2f}->{nl:5.2f} s ({nl - ol:+.2f}) | "
              f"src {osi:.2f}-{oso:.2f} -> {si:.2f}-{so:.2f} | vol {o.get('volume')}->{e.get('volume')}")
for i in oid - lid:
    o = old[i]
    if inside(o):
        print(f"  REMOVED {name(i):24} @{o['startTime']:8.2f} len {o['endTime'] - o['startTime']:.2f}")
order_old = [e['id'] for e in om if e['id'] in lid]
order_new = [e['id'] for e in lm if e['id'] in oid]
if order_old != order_new:
    print('  ORDER CHANGED: some clips were moved relative to each other')

print('\nOTHER ELEMENTS  (captions, music, adjustment layers)')
for i in sorted(set(old) | set(after_els), key=lambda k: (after_els.get(k) or old.get(k))['startTime']):
    if i in oid or i in lid:
        continue
    o, n = old.get(i), after_els.get(i)
    e = n or o
    if not inside(e) and not (o and inside(o)):
        continue
    kind = e.get('content') or e.get('sourceMediaType') or '?'
    label = (e.get('text') or e.get('title') or e.get('effectDisplayName') or e.get('name') or '')[:50]
    if not o:
        print(f"  ADDED   {kind:10} @{n['startTime']:8.2f}-{n['endTime']:8.2f} {label}")
    elif not n:
        print(f"  REMOVED {kind:10} @{o['startTime']:8.2f}-{o['endTime']:8.2f} {label}")
    else:
        ch = [k for k in ('startTime', 'endTime', 'volume', 'text') if k in n and n.get(k) != o.get(k)
              and not (isinstance(n.get(k), (int, float)) and abs(n[k] - (o.get(k) or 0)) < 0.02)]
        if ch:
            print(f"  {kind:10} {label:50} " + ', '.join(f"{k} {o.get(k)!r}->{n.get(k)!r}" for k in ch))
