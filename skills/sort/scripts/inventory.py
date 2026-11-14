"""READ-ONLY inventory of a footage folder, for setup: clips per folder, total minutes, formats, the camera each file
names, and broken or 0-second files. Never changes a file.
  python3 -I inventory.py <footage folder> [--depth 2] [--json out.json] [--workers 8]
--depth groups by that many folder levels under the root (2 = e.g. City/date). Videos only; photos are counted.
The camera model comes from the file's own tags (DJI writes it as the encoder, phones as make/model). Colour tags are
listed as the file reports them: many log cameras still tag their files Rec.709, so check a frame before deciding."""
import sys, os, json, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from footage_lib import media_files, kind, probe, shot_time, camera, fmt_dur

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


depth = opt('--depth', 2, int)
out_json = opt('--json')
workers = opt('--workers', 8, int)
if len(a) != 1:
    sys.exit(__doc__)
root = os.path.abspath(a[0])
files = media_files(root)
videos = [f for f in files if kind(f) == 'video']
photos = len(files) - len(videos)
with ThreadPoolExecutor(workers) as ex:
    infos = list(ex.map(probe, videos))
rows = []
for f, i in zip(videos, infos):
    rel = os.path.relpath(f, root).split(os.sep)
    dt, src = shot_time(f, i)
    rows.append({'path': f, 'group': '/'.join(rel[:-1][:depth]) or '.', 'duration': i.get('duration') or 0,
                 'format': f"{i.get('width')}x{i.get('height')} {i.get('fps')} fps {i.get('codec')} {i.get('pix_fmt')}",
                 'colour_tags': f"{i.get('primaries') or '-'} / {i.get('transfer') or '-'}", 'camera': camera(i),
                 'shot': dt.isoformat(timespec='seconds'), 'time_source': src,
                 'broken': not i or (i.get('duration') or 0) < 0.5})
groups = collections.defaultdict(list)
for r in rows:
    groups[r['group']].append(r)
print(f"{'folder':44} clips    length")
for g in sorted(groups):
    print(f"{g[:44]:44} {len(groups[g]):5}  {fmt_dur(sum(r['duration'] for r in groups[g])):>8}")
print(f"{'TOTAL':44} {len(rows):5}  {fmt_dur(sum(r['duration'] for r in rows)):>8}   (+ {photos} photos)")
for label, key in (('Formats', 'format'), ('Cameras', 'camera'), ('Colour tags (primaries / transfer)', 'colour_tags'),
                   ('Shooting time from', 'time_source')):
    print(f'{label}:')
    for v, n in collections.Counter(r[key] or 'not named in the file' for r in rows if not r['broken']).most_common():
        print(f'  {n:5}  {v}')
bad = [r for r in rows if r['broken']]
print(f'Broken or under 0.5 s: {len(bad)}')
for r in bad:
    print('  ', os.path.relpath(r['path'], root), f"({os.path.getsize(r['path'])} bytes)")
if out_json:
    json.dump(rows, open(out_json, 'w'), indent=1)
    print('wrote', out_json)
