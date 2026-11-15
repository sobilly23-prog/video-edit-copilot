"""READ-ONLY sound check: finds the places a viewer hears the sound drop out, go almost silent, cut in or cut out hard,
or jump in level across a cut. Viewers notice these far more than a cut that's a frame late.
  python3 -I sound_scan.py <audio or video file> [--start S] [--snapshot snapshot.json] [--from T0] [--to T1]
                           [--json out.json]
Run it on the exported film before publishing, and on a rendered stretch (render_audio.py) after every build, every
review round and every pass of the user's own, because their trims move the sound seams.
  --start S       the timeline time (s) the file starts at, when it's a rendered stretch rather than the whole film
  --snapshot F    a snapshot.py file, so each finding says whether it sits ON a cut (the edit caused it) or MID-SHOT
                  (nothing was cut there: the source or the render)
Finds, in timeline seconds:
  DROPOUT  below -55 dBFS for 0.10 s or more (true silence: a muted shot with no music, a gap, a silent song intro)
  QUIET    below -48 dBFS for 0.40 s or more (near-silence a viewer hears as "the sound went")
  CUT-IN   up 18 dB or more within 10 ms, out of quiet (a clip's sound starting hard, with no fade)
  CUT-OUT  down 18 dB or more within 10 ms, into quiet (a clip's sound stopping hard)
  JUMP     with --snapshot: the level 0.3 s each side of a main-track cut differs by 8 dB or more
Not every finding is a mistake: silence can be meant. Give each one a verdict (intentional, accidental, unsure) per
music-and-sound.md in the refine skill. Never edits anything."""
import sys, os, json, math, shutil, subprocess
from array import array
from collections import Counter

a = sys.argv[1:]
if not a or a[0].startswith('-'):
    sys.exit(__doc__)
src = a[0]
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
START, T0, T1 = float(opt('--start', 0)), float(opt('--from', -1e9)), float(opt('--to', 1e9))
SR, WIN = 8000, 80                                   # 10 ms windows
FF = shutil.which('ffmpeg') or sys.exit('ffmpeg not found: see the setup skill')
raw = subprocess.run([FF, '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
x = array('h')
x.frombytes(raw[:len(raw) // 2 * 2])
n = len(x) // WIN
if not n:
    sys.exit(f'{src}: no audio found')
L = []
for i in range(n):
    w = x[i * WIN:(i + 1) * WIN]
    L.append(10 * math.log10(sum(v * v for v in w) / WIN / 1073741824.0 + 1e-12))   # dBFS
tl = lambda i: START + i * WIN / SR

cuts = []
if opt('--snapshot'):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from edits_api import main_track                 # pure function: no app connection needed
    snap = json.load(open(opt('--snapshot')))
    cuts = sorted({round(e['startTime'], 4) for e in main_track({e['id']: e for e in snap['elements']})[1:]})


def where(t):
    if not cuts:
        return ''
    c = min(cuts, key=lambda c: abs(c - t))
    return f'ON cut {c:.3f}' if abs(c - t) <= 0.06 else f'MID-SHOT (nearest cut {c:.3f}, {t - c:+.2f} s)'


found = []


def runs(th, mind, kind):
    i = 0
    while i < n:
        if L[i] >= th:
            i += 1
            continue
        j = i
        while j < n and L[j] < th:
            j += 1
        if (j - i) * WIN / SR >= mind and T0 <= tl(i) <= T1:
            found.append({'kind': kind, 't': round(tl(i), 3), 'end': round(tl(j), 3),
                          'dur': round((j - i) * WIN / SR, 2), 'level': round(min(L[i:j]), 1),
                          'where': where(tl(i)) + (' / ' + where(tl(j)) if cuts else '')})
        i = j


runs(-55, 0.10, 'DROPOUT')
runs(-48, 0.40, 'QUIET')
for i in range(3, n - 3):
    t = tl(i)
    if not (T0 <= t <= T1):
        continue
    before = max(L[i - 3:i])
    if L[i] - before >= 18 and L[i] > -42:
        found.append({'kind': 'CUT-IN', 't': round(t, 3), 'from': round(before, 1), 'to': round(L[i], 1),
                      'where': where(t)})
    after = max(L[i + 1:i + 4])
    if L[i] - after >= 18 and L[i] > -42:
        found.append({'kind': 'CUT-OUT', 't': round(tl(i + 1), 3), 'from': round(L[i], 1), 'to': round(after, 1),
                      'where': where(tl(i + 1))})


def short_term(t0, t1):
    i0, i1 = max(0, int((t0 - START) * SR / WIN)), min(n, int((t1 - START) * SR / WIN))
    if i1 <= i0:
        return None
    return 10 * math.log10(sum(10 ** (v / 10) for v in L[i0:i1]) / (i1 - i0) + 1e-12)


for c in cuts:
    if not (T0 <= c <= T1) or c - START < 0.3 or c - START > n * WIN / SR - 0.3:
        continue
    b, f = short_term(c - 0.3, c - 0.02), short_term(c + 0.02, c + 0.3)
    if b is not None and f is not None and abs(f - b) >= 8:
        found.append({'kind': 'JUMP', 't': round(c, 3), 'from': round(b, 1), 'to': round(f, 1), 'where': 'ON cut'})

found.sort(key=lambda f: f['t'])
cnt = Counter(f['kind'] for f in found)
print(f"{os.path.basename(src)}: {n * WIN / SR:.1f} s scanned (timeline {START:.1f}-{START + n * WIN / SR:.1f}), "
      f"{len(cuts)} cuts known | " + (', '.join(f'{k} {v}' for k, v in sorted(cnt.items())) or 'clean'))
for f in found:
    t = f['t']
    print(f"  {f['kind']:8s} {int(t // 60)}:{t % 60:05.2f} ({t:.2f})", {k: v for k, v in f.items() if k not in ('kind', 't')})
if opt('--json'):
    json.dump(found, open(opt('--json'), 'w'), indent=1)
