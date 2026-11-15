"""Frame audio transitions: a tiny audio fade (about 2 frames) on both sides of every cut where the sound jumps, so one
shot's sound hands over to the next without a click or a hard edge. The picture stays a hard cut (setFade is audio).
  python3 -I audio_fades.py "<exact title>" <t0> <t1> [--sec 0.083] [--check] [--snapshot snapshot.json]
Every main-track clip with sound starting in [t0, t1) gets fadeIn/fadeOut = max(its current fade, --sec).
  - A continuous split gets no fade: the same source file, the next piece starting where the last one stopped, so the
    sound never jumped and a fade would only make a dip.
  - Longer fades (an ending, a chosen fade) are kept. Muted and 0-volume clips are skipped.
  --check     read-only audit: lists clips with sound that are missing a fade at a jump cut, and continuous splits
              that carry a fade (a dip). Zero missing is the goal.
  --snapshot  audit a snapshot.py file instead of the open project (with --check; source files come from clipmap.json).
Re-run it after every build, every review round and every pass of the user's own (their splits and trims add cuts),
and before export."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard, elements, main_track, src_in

a = sys.argv[1:]
if len(a) < 3 or a[0].startswith('-'):
    sys.exit(__doc__)
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
check, snap_path = '--check' in a, opt('--snapshot')
if snap_path and not check:
    sys.exit('--snapshot only works with --check (it audits a file, it never edits one).')
TITLE, t0, t1 = a[0], float(a[1]), float(a[2])
sec = float(opt('--sec', 2 / 24))
enough = sec * 0.9                                    # a fade within 10% of --sec counts (0.08 s is 2 frames too)
if snap_path:
    clips = main_track({e['id']: e for e in json.load(open(snap_path))['elements']})
else:
    guard(TITLE)
    clips = main_track(elements())

cmap_path = os.path.join('video-edit-copilot', 'clipmap.json')
cmap = json.load(open(cmap_path)) if os.path.exists(cmap_path) else {}


def source(e):
    if e['id'] not in cmap:
        if snap_path:
            return None                               # offline: unknown source, so treat every cut as a jump
        cmap[e['id']] = {'path': call('clipMetadata', id=e['id']).get('path')}
    return cmap[e['id']].get('path')


def has_sound(e):
    return (e.get('volume') or 0) > 0.001 and not e.get('isMuted')


def continuous(p, q):
    """p then q is one take split in two: same file, q picks up where p stopped, no gap on the timeline."""
    if not p or not q or abs(p['startTime'] + p['duration'] - q['startTime']) > 0.02:
        return False
    sp, sq = source(p), source(q)
    p_out = p.get('sourceOutPoint', src_in(p) + p['duration'] * (p.get('speed') or 1))
    return bool(sp) and sp == sq and abs(p_out - src_in(q)) < 0.02


missing, dips, n = [], [], 0
for i, e in enumerate(clips):
    if not (t0 - 1e-3 <= e['startTime'] < t1) or not has_sound(e):
        continue
    prev = clips[i - 1] if i else None
    nxt = clips[i + 1] if i + 1 < len(clips) else None
    need_in, need_out = not continuous(prev, e), not continuous(e, nxt)
    fi, fo = e.get('fadeIn') or 0, e.get('fadeOut') or 0
    if check:
        for side, need, cur in (('in', need_in, fi), ('out', need_out, fo)):
            if need and cur < enough:
                missing.append((e['startTime'], e['id'][:8], side, cur))
            if not need and cur > 1e-3:
                dips.append((e['startTime'], e['id'][:8], side, cur))
        continue
    new_in = sec if need_in and fi < enough else fi
    new_out = sec if need_out and fo < enough else fo
    if abs(new_in - fi) > 1e-4 or abs(new_out - fo) > 1e-4:
        call('setFade', id=e['id'], fadeIn=round(new_in, 4), fadeOut=round(new_out, 4))
        n += 1

if os.path.isdir('video-edit-copilot') and cmap and not snap_path:
    json.dump(cmap, open(cmap_path, 'w'), indent=0)
if check:
    for t, i8, side, cur in missing:
        print(f'  MISSING  {int(t // 60)}:{t % 60:05.2f}  {i8}  fade-{side} {cur:.3f} s')
    for t, i8, side, cur in dips:
        print(f'  DIP      {int(t // 60)}:{t % 60:05.2f}  {i8}  fade-{side} {cur:.3f} s on a continuous split')
    print(f'{len(missing)} clips with sound missing a fade, {len(dips)} fades on continuous splits '
          f'(between {t0} and {t1} s)')
else:
    call('saveProject')
    print(f'{n} clips got audio fades of {sec:.3f} s between {t0} and {t1} s')
