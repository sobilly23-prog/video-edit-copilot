"""Render a stretch of the timeline's sound to one .wav, through Edits' own preview renderer (up to 10 s per render,
joined). It's the mix the viewer will hear: clip volumes, fades, music and library songs, which have no readable file.
  python3 -I render_audio.py <out.wav> <start s> <length s> ["<exact title>"]
Then check it: `sound_scan.py out.wav --start <start s> --snapshot snapshot.json`. Read-only on the project (it only
renders previews), but it takes about real time, so render the stretch you changed rather than the whole film."""
import sys, os, time, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard

if len(sys.argv) < 4:
    sys.exit(__doc__)
out, start, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
if len(sys.argv) > 4:
    guard(sys.argv[4])
FF = shutil.which('ffmpeg') or sys.exit('ffmpeg not found: see the setup skill')
tmp = tempfile.mkdtemp(prefix='render_audio_')
parts, t = [], start
while t < start + dur - 0.05:
    d = min(10.0, start + dur - t)
    r = call('previewVideo', startSeconds=round(t, 3), durationSeconds=round(d, 3), frameCount=1, maxWidth=160,
             clipMaxWidth=160, includeClip=True)
    rid, s = r.get('resultId'), {}
    for _ in range(240):
        s = call('previewVideoStatus')
        if not s.get('rendering') and (rid is None or s.get('resultId') == rid):
            break
        time.sleep(0.5)
    clip = s.get('clip') or (s.get('result') or {}).get('clip') or {}
    p = clip.get('path')
    if not s.get('ok', True) or not p or not os.path.exists(p):
        sys.exit(f'render failed at {t:.2f} s: {s}')
    w = os.path.join(tmp, f'{len(parts):04d}.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', p, '-vn', '-ac', '2', '-ar', '48000', '-t', f'{d:.3f}', w], check=True)
    parts.append(w)
    t += d
lst = os.path.join(tmp, 'list.txt')
with open(lst, 'w') as f:
    f.write(''.join(f"file '{p}'\n" for p in parts))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f'wrote {out}: {len(parts)} renders, {dur:.1f} s from {start:.1f} s')
