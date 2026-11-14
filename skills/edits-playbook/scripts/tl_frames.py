"""READ-ONLY: CLEAN graded frames (no captions) at TIMELINE times, pulled straight from the source files with ffmpeg.
  python3 -I tl_frames.py <snapshot.json> <out_dir> <t | t0-t1[/step]> ... [--w 480] [--sheet name.jpg --cols 6]
Needs video-edit-copilot/clipmap.json (run clipmap.py first). Log clips get the conversion LUT from settings.json
("log_lut", applied to files whose names match "log_sources"), so frames show real colour. Vertical (phone) clips are
centred on a 16:9 frame. Use for analysis, review sheets and picks pages; it never moves the app's playhead."""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import main_track, settings, src_in

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


W = opt('--w', 480, int)
H = W * 9 // 16
sheet = opt('--sheet')
cols = opt('--cols', 6, int)
if len(a) < 3:
    sys.exit(__doc__)
snap, out, specs = json.load(open(a[0])), a[1], a[2:]
cfg = settings()
lut = cfg.get('log_lut') or ''
if lut and not os.path.exists(lut):
    print(f'warning: log_lut not found ({lut}); frames will be ungraded (is the drive with your LUTs connected?)')
    lut = ''
log_pats = [re.compile(p) for p in cfg.get('log_sources') or []]
cmap = json.load(open(os.path.join(os.getcwd(), 'video-edit-copilot', 'clipmap.json')))
mt = main_track({e['id']: e for e in snap['elements']})
os.makedirs(out, exist_ok=True)

times = []
for s in specs:
    if '-' in s.lstrip('-'):
        rng, _, st = s.partition('/')
        t0, t1 = map(float, rng.split('-'))
        t, st = t0, float(st or 1.5)
        while t <= t1 + 1e-6:
            times.append(round(t, 3)); t += st
    else:
        times.append(float(s))

files, idx = [], []
for t in times:
    e = next((c for c in mt if c['startTime'] <= t < c['endTime']), None)
    if not e:
        continue
    src = src_in(e) + (t - e['startTime']) * (e.get('speed') or 1)
    m = cmap.get(e['id'], {})
    path, name = m.get('path'), m.get('name') or ''
    is_log = bool(lut) and any(p.search(name) for p in log_pats)
    vf = f'scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1'
    if is_log:
        vf = f"lut3d='{lut}'," + vf
    f = os.path.join(out, f'tl_{t:08.2f}.jpg')
    if path and not os.path.exists(path):
        print(f'missing source for {t:.2f}: {path}')
    elif path and not os.path.exists(f):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(src, 0):.3f}', '-i', path, '-frames:v', '1', '-vf', vf, f])
    if os.path.exists(f):
        files.append(f)
        idx.append(f'{len(files)}: tl {t:.2f}  {name}  src {src:.2f}  id {e["id"][:8]}')
print('\n'.join(idx))
if sheet and files:
    lst = os.path.join(out, '_sheet.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
    rows = (len(files) + cols - 1) // cols
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', f'tile={cols}x{rows}',
                    '-frames:v', '1', os.path.join(out, sheet)], check=True)
    open(os.path.join(out, sheet[:-4] + '.txt'), 'w').write('\n'.join(idx) + '\n')
    print('sheet', os.path.join(out, sheet))
