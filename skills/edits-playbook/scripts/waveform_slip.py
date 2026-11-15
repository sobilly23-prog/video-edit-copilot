"""Waveform cuts on a film that's already built: slip shots (same place, same length, different moment of the source) so
both of a shot's cuts land on quieter moments. Nothing ripples: captions and music stay where they are.
  python3 -I waveform_slip.py "<exact title>" <t0> <t1> [--window 0.21] [--min-gain 6] [--mine build-log.json]
                              [--skip id8,id8] [--dry]
For every main-track clip with sound starting in [t0, t1): read the source's loudness around its in and out points and
pick one slip (whole frames, at most --window s either way) that lowers the louder of its two ends by at least
--min-gain dB. Uses `slipClip`, which keeps the shot's timeline place and length.
  --mine F   only slip shots the copilot built (their ids are in build_cut.py's build-log.json). The user's own cuts are
             listed for them to decide instead, never changed.
  --dry      list what it would do and change nothing (always do this first).
Speech isn't checked here: keep it to stretches where speech is already muted or avoided. Run after the user's passes
too, since their trims add cuts."""
import sys, os, json, math, shutil, subprocess
from array import array
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard, elements, main_track, src_in

a = sys.argv[1:]
if len(a) < 3 or a[0].startswith('-'):
    sys.exit(__doc__)
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
TITLE, t0, t1 = a[0], float(a[1]), float(a[2])
W, G, dry = float(opt('--window', 0.21)), float(opt('--min-gain', 6.0)), '--dry' in a
skip = set(opt('--skip', '').split(',')) - {''}
mine = {r['id'] for r in json.load(open(opt('--mine')))['shots']} if opt('--mine') else None
FF = shutil.which('ffmpeg') or sys.exit('ffmpeg not found: see the setup skill')
FP = shutil.which('ffprobe') or sys.exit('ffprobe not found: see the setup skill')
guard(TITLE)

cmap_path = os.path.join('video-edit-copilot', 'clipmap.json')
cmap = json.load(open(cmap_path)) if os.path.exists(cmap_path) else {}


def source(eid):
    if eid not in cmap:
        cmap[eid] = {'path': call('clipMetadata', id=eid).get('path')}
    return cmap[eid].get('path')


def fps(path):
    r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                        '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    try:
        num, den = (r.split('/') + ['1'])[:2]
        return float(num) / float(den) or 24.0
    except (ValueError, ZeroDivisionError):
        return 24.0


def levels(path, start, dur, sr=8000, win=80):
    start = max(0.0, start)
    raw = subprocess.run([FF, '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{dur:.3f}', '-i', path, '-vn', '-ac', '1',
                          '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout
    x = array('h')
    x.frombytes(raw[:len(raw) // 2 * 2])
    return [(start + i * win / sr, 10 * math.log10(sum(v * v for v in x[i * win:(i + 1) * win]) / win / 1073741824.0
                                                    + 1e-12)) for i in range(len(x) // win)]


def at(env, t):
    return min(env, key=lambda sv: abs(sv[0] - t))[1] if env else -90.0


slipped, theirs = 0, []
for e in main_track(elements()):
    if not (t0 - 1e-3 <= e['startTime'] < t1) or e['id'][:8] in skip:
        continue
    if (e.get('volume') or 0) <= 0.001 or e.get('isMuted'):
        continue
    path = source(e['id'])
    if not path or not os.path.exists(path):
        print(f"  {e['id'][:8]} @{e['startTime']:.3f}: source file not found, skipped")
        continue
    si = src_in(e)
    so = e.get('sourceOutPoint', si + e['duration'] * (e.get('speed') or 1))
    dur = e.get('sourceDuration') or 1e9
    ei, eo = levels(path, si - W, 2 * W + 0.02), levels(path, so - W, 2 * W + 0.02)
    f = fps(path)
    end_level = lambda d: max(at(ei, si + d), at(eo, so + d))
    cur, best = end_level(0), 0.0
    for k in range(-int(W * f), int(W * f) + 1):
        d = k / f
        if si + d >= 0 and so + d <= dur and end_level(d) < cur - G and end_level(d) < end_level(best):
            best = d
    if not best:
        continue
    line = (f"{e['id'][:8]} @{e['startTime']:8.3f}  source {si:.3f}-{so:.3f}  slip {best:+.3f} s  "
            f"louder end {cur:.1f} dB -> {end_level(best):.1f} dB")
    if mine is not None and e['id'] not in mine:
        theirs.append(line)
        continue
    print('  ' + line)
    slipped += 1
    if not dry:
        call('slipClip', id=e['id'], deltaSeconds=round(best, 4))

if os.path.isdir('video-edit-copilot') and cmap:
    json.dump(cmap, open(cmap_path, 'w'), indent=0)
if not dry and slipped:
    call('saveProject')
print(f"{slipped} shots {'would be ' if dry else ''}slipped between {t0} and {t1} s")
if theirs:
    print(f'{len(theirs)} of the user\'s own cuts land on a loud moment. Show them on the review page; don\'t change them:')
    for line in theirs:
        print('  ' + line)
