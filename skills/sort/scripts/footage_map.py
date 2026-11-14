"""READ-ONLY. A one-page visual map of a footage folder: a strip of frames for every clip (log clips converted so the
colours are real), grouped by folder, with when each was shot and how long it runs. Also writes <out>.json, the clip
index that sort_footage.py and the first cut use.
  python3 -I footage_map.py <footage folder> <out.html> [--frames 5] [--h 96] [--workers 4]
                            [--lut file.cube --log-pattern REGEX]   (default: log_lut / log_sources from settings.json)
Images are embedded, so the page is one file you can open or publish. Needs ffmpeg and ffprobe (and macOS `sips` for
HEIC photos)."""
import sys, os, re, json, base64, html, shutil, tempfile, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from footage_lib import media_files, kind, probe, shot_time, trip_day, settings, fmt_dur

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


N = opt('--frames', 5, int)
H = opt('--h', 96, int)
WORKERS = opt('--workers', 4, int)
cfg = settings()
LUT = opt('--lut', cfg.get('log_lut') or '')
pats = [opt('--log-pattern')] if '--log-pattern' in a else (cfg.get('log_sources') or [])
LOG = [re.compile(p) for p in pats if p]
if len(a) != 2:
    sys.exit(__doc__)
ROOT, OUT = os.path.abspath(a[0]), a[1]
if LUT and not os.path.exists(LUT):
    print(f'warning: LUT not found ({LUT}); log clips will look flat'); LUT = ''
tmp = tempfile.mkdtemp(prefix='footage_map_')
lut_safe = ''
if LUT:                                   # ffmpeg filter paths can't easily hold spaces or colons: use a safe copy
    lut_safe = os.path.join(tmp, 'log.cube'); shutil.copy(LUT, lut_safe)


def is_log(p):
    return bool(LOG) and any(r.search(os.path.basename(p)) for r in LOG)


def strip(p, info):
    """JPEG bytes of N frames side by side (or one frame for a photo)."""
    if kind(p) == 'photo':
        src = p
        if os.path.splitext(p)[1].lower() in ('.heic', '.heif', '.dng') and shutil.which('sips'):
            src = os.path.join(tmp, os.path.basename(p) + '.jpg')
            subprocess.run(['sips', '-s', 'format', 'jpeg', '-Z', str(H * 4), p, '--out', src], capture_output=True)
        cmd = ['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale=-2:{H}', '-frames:v', '1', '-f', 'image2pipe',
               '-vcodec', 'mjpeg', '-q:v', '5', '-']
    else:
        d = info.get('duration') or 0
        if d <= 0:
            return b''
        ts = [d * (i + 0.5) / N for i in range(N)]
        cmd = ['ffmpeg', '-v', 'error']
        for t in ts:
            cmd += ['-ss', f'{t:.2f}', '-i', p]
        chain = (f',lut3d=file={lut_safe}' if lut_safe and is_log(p) else '')
        parts = ''.join(f'[{i}:v]scale=-2:{H}{chain},setsar=1[v{i}];' for i in range(N))
        fc = parts + ''.join(f'[v{i}]' for i in range(N)) + f'hstack=inputs={N}[out]'
        cmd += ['-filter_complex', fc, '-map', '[out]', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'mjpeg',
                '-q:v', '5', '-']
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    return r.stdout if r.returncode == 0 else b''


def one(p):
    info = probe(p) if kind(p) == 'video' else {}
    dt, src = shot_time(p, info)
    return {'path': p, 'rel': os.path.relpath(p, ROOT), 'folder': os.path.relpath(os.path.dirname(p), ROOT),
            'kind': kind(p), 'duration': info.get('duration', 0), 'width': info.get('width'),
            'height': info.get('height'), 'fps': info.get('fps'), 'codec': info.get('codec'), 'log': is_log(p),
            'shot': dt.isoformat(timespec='seconds'), 'time_source': src, 'day': trip_day(dt).isoformat(),
            'img': base64.b64encode(strip(p, info)).decode()}


files = media_files(ROOT)
if not files:
    sys.exit(f'No video or photo files under {ROOT}')
print(f'{len(files)} files, {WORKERS} at a time…', flush=True)
with ThreadPoolExecutor(WORKERS) as ex:
    clips = list(ex.map(one, files))
shutil.rmtree(tmp, ignore_errors=True)

json.dump([{k: v for k, v in c.items() if k != 'img'} for c in clips], open(os.path.splitext(OUT)[0] + '.json', 'w'),
          indent=1)

groups = {}
for c in sorted(clips, key=lambda c: c['shot']):           # folders in the order they were shot, so the page reads
    groups.setdefault(c['folder'], []).append(c)             # like the trip
total = sum(c['duration'] for c in clips)
rows = []
for folder, cs in groups.items():
    cs.sort(key=lambda c: c['shot'])
    dur = sum(c['duration'] for c in cs)
    t0, t1 = cs[0]['shot'][:16].replace('T', ' '), cs[-1]['shot'][11:16]
    rows.append(f'<section><h2>{html.escape(folder if folder != "." else os.path.basename(ROOT))}</h2>'
                f'<p class="meta">{len(cs)} files · {fmt_dur(dur)} · {t0}–{t1}</p>')
    prev = None
    for c in cs:
        dt = datetime.datetime.fromisoformat(c['shot'])
        if prev and (dt - prev).total_seconds() > 20 * 60:
            rows.append(f'<div class="gap">{int((dt - prev).total_seconds() // 60)} min later</div>')
        prev = dt
        size = f'{c["width"]}×{c["height"]}' if c['width'] else ''
        tags = ' · '.join(x for x in [c['shot'][11:19], fmt_dur(c['duration']) if c['kind'] == 'video' else 'photo',
                                      size, 'log' if c['log'] else ''] if x)
        img = (f'<img loading="lazy" src="data:image/jpeg;base64,{c["img"]}" alt="{html.escape(c["rel"])}">'
               if c['img'] else '<span class="noimg">no preview</span>')
        rows.append(f'<div class="clip"><div class="name">{html.escape(os.path.basename(c["rel"]))}'
                    f'<span>{tags}</span></div>{img}</div>')
    rows.append('</section>')

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Footage Map</title>
<style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--muted:#6b6a66;--line:#e2e0da;--accent:#8a6d1f}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#151514;--card:#1f1f1d;--ink:#ecebe7;--muted:#a3a19b;--line:#33322f;--accent:#d9b65a}}}}
:root[data-theme="dark"]{{--bg:#151514;--card:#1f1f1d;--ink:#ecebe7;--muted:#a3a19b;--line:#33322f;--accent:#d9b65a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 64px}}
h1{{font-size:26px;margin:0 0 4px}} .lede{{color:var(--muted);margin:0 0 24px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 20px}}
h2{{font-size:18px;margin:0}} .meta{{color:var(--muted);margin:2px 0 12px;font-size:13px}}
.clip{{margin:0 0 12px}} .clip img{{display:block;max-width:100%;height:auto;border-radius:6px}}
.name{{font-size:13px;font-weight:600;margin:0 0 4px;overflow-wrap:anywhere}}
.name span{{font-weight:400;color:var(--muted);margin-left:8px}}
.gap{{font-size:12px;color:var(--accent);border-top:1px dashed var(--line);margin:14px 0 10px;padding-top:6px}}
.noimg{{font-size:12px;color:var(--muted)}}
</style></head><body><main>
<h1>Footage map</h1>
<p class="lede">{html.escape(os.path.basename(ROOT))} · {len(clips)} files · {fmt_dur(total)} of video ·
{len(groups)} folders. Frames are spread evenly through each clip{', with log clips converted' if lut_safe else ''}.
A dashed line marks a gap of 20+ minutes, which usually means a new place.</p>
{''.join(rows)}
</main></body></html>"""
open(OUT, 'w').write(PAGE)
print(f'wrote {OUT} ({os.path.getsize(OUT) / 1e6:.1f} MB) and {os.path.splitext(OUT)[0]}.json')
