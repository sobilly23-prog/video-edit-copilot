"""READ-ONLY: study an example video the user likes, so the copilot can learn a style it wasn't built for.
  python3 -I analyse_reference.py <video file> [--out <folder>] [--threshold 0.3] [--max-frames 24]
Reports, and saves to <out>/analysis.json:
  - length, frame size, aspect (16:9, 9:16 ...), frame rate
  - shots, from scene-change detection: cuts per minute, shot length (median, mean, shortest, longest), and how long
    the first shot holds (the hook)
  - sound: integrated loudness, loudness range, and the share of near-silence
Also writes <out>/shots.jpg (the first frame of each shot, up to --max-frames, picked evenly) and <out>/hook.jpg (the
first 3 seconds, every 0.5 s).
Scene detection misses slow dissolves and can count flashes as cuts, so treat the numbers as approximate and check the
sheets. Lower --threshold (e.g. 0.2) if it misses cuts between similar shots. Reads the file only; never uploads or
downloads anything. Needs ffmpeg and ffprobe."""
import sys, os, re, json, shutil, statistics, subprocess, tempfile

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


threshold = opt('--threshold', 0.3, float)
max_frames = opt('--max-frames', 24, int)
out = opt('--out')
if len(a) != 1 or not os.path.isfile(a[0]):
    sys.exit(__doc__)
src = os.path.abspath(a[0])
out = os.path.abspath(out or os.path.splitext(os.path.basename(src))[0] + '_analysis')
os.makedirs(out, exist_ok=True)


def run(cmd, timeout=3600):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# 1. format
r = run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', src])
info = json.loads(r.stdout or '{}')
v = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
if not v:
    sys.exit('No video stream found.')
has_audio = any(s.get('codec_type') == 'audio' for s in info.get('streams', []))
w, h = int(v.get('width') or 0), int(v.get('height') or 0)
for sd in v.get('side_data_list') or []:
    if 'rotation' in sd and abs(int(float(sd['rotation']))) in (90, 270):
        w, h = h, w
duration = float(info.get('format', {}).get('duration') or v.get('duration') or 0)
n, d = (v.get('avg_frame_rate') or '0/1').split('/')
fps = round(float(n) / float(d), 3) if float(d) else 0
ratio = w / h if h else 0
named = {'16:9': 16 / 9, '9:16': 9 / 16, '4:5': 4 / 5, '1:1': 1.0, '4:3': 4 / 3, '21:9': 21 / 9, '2.39:1': 2.39}
aspect = min(named, key=lambda k: abs(named[k] - ratio)) if ratio else '?'

# 2. cuts
r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-an', '-vf',
         f"scale=320:-2,select='gt(scene,{threshold})',showinfo", '-f', 'null', '-'])
cuts = []
for t in (float(x) for x in re.findall(r'pts_time:([\d.]+)', r.stderr)):
    if 0.25 < t < duration - 0.1 and (not cuts or t - cuts[-1] >= 0.25):   # ignore flashes under 0.25 s
        cuts.append(round(t, 3))
bounds = [0.0] + cuts + [duration]
shots = [round(bounds[i + 1] - bounds[i], 3) for i in range(len(bounds) - 1)]

# 3. sound
loud = {'integrated_lufs': None, 'loudness_range_lu': None, 'near_silence_share': None}
if has_audio:
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-vn', '-af',
             'ebur128,silencedetect=n=-45dB:d=0.5', '-f', 'null', '-'])
    i_vals, lra = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr), re.findall(r'LRA:\s+([\d.]+) LU', r.stderr)
    silent = sum(float(x) for x in re.findall(r'silence_duration: ([\d.]+)', r.stderr))
    loud = {'integrated_lufs': float(i_vals[-1]) if i_vals else None,
            'loudness_range_lu': float(lra[-1]) if lra else None,
            'near_silence_share': round(silent / duration, 3) if duration else None}

# 4. sheets
can_label = 'drawtext' in run(['ffmpeg', '-hide_banner', '-filters']).stdout


def sheet(times, path, cols):
    tmp = tempfile.mkdtemp(prefix='ref_')
    try:
        for k, t in enumerate(times):
            vf = 'scale=320:-2' if w >= h else 'scale=-2:320'      # every frame the same size, in the video's shape
            if can_label:
                vf += f",drawtext=text='{t:.1f}s':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6"
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', '-vf', vf,
                 os.path.join(tmp, f'f{k:03d}.jpg')])
        frames = sorted(f for f in os.listdir(tmp) if f.endswith('.jpg'))
        if not frames:
            return None
        rows = (len(frames) + cols - 1) // cols
        run(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-i', os.path.join(tmp, 'f%03d.jpg'),
             '-vf', f'tile={cols}x{rows}:padding=4:color=black', '-frames:v', '1', '-q:v', '4', path])
        return path if os.path.exists(path) else None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


starts = [min(b + 0.15, duration - 0.05) for b in bounds[:-1]]
if len(starts) > max_frames:
    step = (len(starts) - 1) / (max_frames - 1)
    starts = [starts[round(i * step)] for i in range(max_frames)]
shots_jpg = sheet(starts, os.path.join(out, 'shots.jpg'), 6)
hook_jpg = sheet([t / 2 for t in range(0, 7) if t / 2 < duration], os.path.join(out, 'hook.jpg'), 7)

res = {
    'file': src, 'length_s': round(duration, 2), 'size': f'{w}x{h}', 'aspect': aspect, 'fps': fps,
    'shots': len(shots), 'cuts_per_minute': round(len(cuts) / (duration / 60), 1) if duration else None,
    'shot_length_s': {'median': round(statistics.median(shots), 2), 'mean': round(statistics.mean(shots), 2),
                      'shortest': min(shots), 'longest': max(shots)} if shots else None,
    'first_shot_s': shots[0] if shots else None, 'cut_times_s': cuts, 'threshold': threshold, 'sound': loud,
    'sheets': {'shots': shots_jpg, 'hook': hook_jpg},
}
json.dump(res, open(os.path.join(out, 'analysis.json'), 'w'), indent=1)
sl = res['shot_length_s'] or {}
print(f"{os.path.basename(src)}: {res['length_s']} s, {res['size']} ({aspect}), {fps} fps")
print(f"shots: {res['shots']}  |  {res['cuts_per_minute']} cuts/min  |  shot length median {sl.get('median')} s, "
      f"mean {sl.get('mean')} s, {sl.get('shortest')}-{sl.get('longest')} s  |  first shot {res['first_shot_s']} s")
if has_audio:
    share = loud['near_silence_share']
    print(f"sound: {loud['integrated_lufs']} LUFS, range {loud['loudness_range_lu']} LU, near-silence "
          f"{'-' if share is None else f'{share * 100:.0f}%'}")
else:
    print('sound: no audio track')
print(f"sheets: {shots_jpg}, {hook_jpg}\nsaved: {os.path.join(out, 'analysis.json')}")
