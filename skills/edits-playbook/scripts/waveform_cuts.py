"""Waveform cuts, before building: move every in and out point of a plan onto the quietest moment nearby, so cuts land
between words and between hits (a footstep, a clink) instead of on them.
  python3 -I waveform_cuts.py plan.json [--window 0.25] [--min-len 1.0] [--transcripts DIR] [--dry]
plan.json is the build_cut.py plan: {"scenes": [{"label", "shots": [{"file", "in", "out"}]}]}.
  1. Speech (with --transcripts): if a point falls inside a spoken line of that clip's whole-clip transcript
     (DIR/**/<clip name>*.srt), move it to the line's nearest edge, as long as the shot keeps --min-len.
  2. Waveform: move each point to the quietest 10 ms within +-window s of the source's own sound. Never further than
     the window, never into speech, and the shot keeps at least its planned length - 2 x window (and --min-len).
Points land on whole frames. Writes the plan in place (backup <plan>.pre_waveform.json) and prints every change.
Reads the source files only. Doesn't need the editing app."""
import sys, os, re, json, glob, math, shutil, subprocess
from array import array
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import settings

a = sys.argv[1:]
if not a or a[0].startswith('-'):
    sys.exit(__doc__)
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
plan_path, W, MIN = a[0], float(opt('--window', 0.25)), float(opt('--min-len', 1.0))
tdir, dry = opt('--transcripts'), '--dry' in a
FF = shutil.which('ffmpeg') or sys.exit('ffmpeg not found: see the setup skill')
FP = shutil.which('ffprobe') or sys.exit('ffprobe not found: see the setup skill')
plan = json.load(open(plan_path))
work = settings().get('work_media') or ''
NOISE = re.compile(r'^\s*[\[\(\*].*|thank you|thanks for watching|subscribe|see you in the next|bye\.?$|^\s*$', re.I)


def fps(path):
    r = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                        '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    try:
        num, den = (r.split('/') + ['1'])[:2]
        return float(num) / float(den) or 24.0
    except (ValueError, ZeroDivisionError):
        return 24.0


def levels(path, start, dur, sr=8000, win=80):
    """[(source seconds, dBFS)] in 10 ms steps."""
    start = max(0.0, start)
    raw = subprocess.run([FF, '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{dur:.3f}', '-i', path, '-vn', '-ac', '1',
                          '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout
    x = array('h')
    x.frombytes(raw[:len(raw) // 2 * 2])
    return [(start + i * win / sr, 10 * math.log10(sum(v * v for v in x[i * win:(i + 1) * win]) / win / 1073741824.0
                                                    + 1e-12)) for i in range(len(x) // win)]


def speech(path):
    if not tdir:
        return []
    stem = os.path.splitext(os.path.basename(path))[0]
    f = glob.glob(os.path.join(tdir, '**', f'{glob.escape(stem)}*.srt'), recursive=True)
    if not f:
        return []
    segs = []
    for m in re.finditer(r'(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*?)(?:\n\n|\Z)',
                         open(f[0]).read(), re.S):
        g = [int(v) for v in m.groups()[:8]]
        s0 = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        s1 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        if not NOISE.search(m.group(9).strip()) and s1 - s0 < 25:     # very long single lines are usually invented
            segs.append((s0, s1))
    return segs


def inside(t, segs):
    return next(((s0, s1) for s0, s1 in segs if s0 < t < s1), None)


def quietest(path, t, segs):
    env = [(s, v) for s, v in levels(path, t - W, 2 * W + 0.01) if abs(s - t) <= W and not inside(s, segs)]
    return min(env, key=lambda sv: (round(sv[1], 1), abs(sv[0] - t)))[0] if env else t


changes = []
for sc in plan['scenes']:
    for s in sc['shots']:
        path = s['file'] if os.path.isabs(s['file']) else os.path.join(work, s['file'])
        if not os.path.exists(path):
            print(f"  skipped {s['file']}: file not found")
            continue
        a0, b0 = float(s['in']), float(s['out'])
        x, y, segs = a0, b0, speech(path)
        hit = inside(x, segs)                               # 1. speech
        if hit:
            x = hit[1] if y - hit[1] >= MIN else hit[0]
        hit = inside(y, segs)
        if hit:
            y = hit[0] if hit[0] - x >= MIN else hit[1]
        x, y = max(0.0, quietest(path, x, segs)), quietest(path, y, segs)   # 2. waveform
        if y - x < max(MIN, (b0 - a0) - 2 * W):
            x, y = a0, b0
        f = fps(path)
        x, y = round(round(x * f) / f, 4), round(round(y * f) / f, 4)       # whole frames
        if (x, y) != (a0, b0):
            changes.append((sc.get('label') or '', os.path.basename(path), a0, b0, x, y))
        s['in'], s['out'] = x, y

for c in changes:
    print(f"  {c[0][:22]:<22} {c[1][:28]:<28} {c[2]:>8.3f}-{c[3]:<8.3f} -> {c[4]:>8.3f}-{c[5]:<8.3f} "
          f"({(c[5] - c[4]) - (c[3] - c[2]):+.2f} s)")
print(len(changes), 'cuts moved' + (' (dry run: plan not changed)' if dry else ''))
if not dry and changes:
    shutil.copy(plan_path, re.sub(r'\.json$', '', plan_path) + '.pre_waveform.json')
    plan['waveform_cuts'] = f'applied (window {W} s{", speech-aware" if tdir else ""})'
    json.dump(plan, open(plan_path, 'w'), indent=1)
