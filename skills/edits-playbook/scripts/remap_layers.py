"""Re-fit music, adjustment layers (and optionally captions) to their SCENES after clips changed length.
In Edits, music never moves when the picture changes, and an adjustment piece that spans an edit doesn't stretch, so
after anyone trims, inserts or deletes clips they sit on the wrong shots. This maps each element's start and end from an
OLD snapshot (taken when they were right) onto the live timeline by the nearest main-track cut:
new time = that clip's live start/end + the same offset. An element that ended on the film's end ends on the new end.
  python3 -I remap_layers.py "<project title>" <old_snapshot.json> [--kinds music,adjustment] [--only id8,..]
                             [--skip id8,..] [--keep-length] [--dry]
(--kinds text --keep-length re-seats captions on their shots without changing their length.)
Music keeps its source in-point (where the song starts); its length follows the scene, capped at the song's end.
Run --dry first and read the plan. Re-list music afterwards: a move can report success and not happen."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard, elements, main_track

a = sys.argv[1:]
if len(a) < 2:
    sys.exit(__doc__)
guard(a[0])
old = json.load(open(a[1]))
kinds = set((a[a.index('--kinds') + 1] if '--kinds' in a else 'music,adjustment').split(','))
skip = set(a[a.index('--skip') + 1].split(',')) if '--skip' in a else set()
only = set(a[a.index('--only') + 1].split(',')) if '--only' in a else None
dry, keep = '--dry' in a, '--keep-length' in a

oe = {e['id']: e for e in old['elements']}
omain = main_track(oe)
live = elements()
lmain = {e['id']: e for e in main_track(live)}
bounds = [(e[s], e['id'], s) for e in omain for s in ('startTime', 'endTime')]


def remap(t, prefer):
    for bt, cid, side in sorted(bounds, key=lambda b: (round(abs(t - b[0]), 3), b[2] != prefer)):
        n = lmain.get(cid)
        if n and n['endTime'] - n['startTime'] > 0.1:
            return n[side] + (t - bt), cid[:8], round(t - bt, 3)
    return None, None, None


film_old, film_new = old['duration'], call('state')['duration']
todo = []
for i, o in oe.items():
    if o.get('content') not in kinds or i not in live or i[:8] in skip or (only and i[:8] not in only):
        continue
    if o['startTime'] < 0.01 and abs(o['endTime'] - film_old) < 0.05:
        continue                                   # spans the whole film: stretches by itself
    s, sa, so = remap(o['startTime'], 'startTime')
    e, ea, eo = remap(o['endTime'], 'endTime')
    if abs(o['endTime'] - film_old) < 0.05:
        e, ea, eo = film_new, 'FILM-END', 0
    if s is None or e is None:
        print('  !! no anchor for', i[:8]); continue
    todo.append((o, s, e, f'{sa}{so:+.2f} / {ea}{eo:+.2f}'))

for o, s, e, why in sorted(todo, key=lambda x: -x[0]['startTime']):      # last first: nothing pushed into a neighbour
    i = o['id']
    g = call('getElement', id=i)
    cs, ce = g['startTime'], g['endTime']
    if abs(cs - s) < 0.02 and (keep or abs(ce - e) < 0.02):
        continue
    want = (ce - cs) if keep else e - s
    if o.get('content') == 'music':
        room = (g.get('sourceDuration') or 1e9) - (g.get('sourceInPoint') or 0)
        if want > room:
            print(f'  ! {i[:8]} song too short: wants {want:.2f}s, has {room:.2f}s; ends early'); want = room
    tag = (g.get('title') or g.get('name') or g.get('text') or o.get('content') or '')[:24]
    print(f"{i[:8]} {tag:24} {cs:8.2f}-{ce:8.2f} -> {s:8.2f}-{s + want:8.2f}  [{why}]")
    if dry:
        continue
    if abs((ce - cs) - want) > 0.01:
        call('trim', id=i, side='right', deltaSeconds=(ce - cs) - want)   # positive shortens, negative extends
    call('move', id=i, toSeconds=s)
    g = call('getElement', id=i)
    if abs(g['startTime'] - s) > 0.03 or abs(g['endTime'] - (s + want)) > 0.03:
        print(f"   !! landed {g['startTime']:.2f}-{g['endTime']:.2f}")
if not dry:
    call('saveProject')
print('film', film_new)
