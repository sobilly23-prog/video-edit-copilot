"""READ-ONLY: map every main-track clip in a snapshot to its source file, cached in video-edit-copilot/clipmap.json.
  python3 -I clipmap.py <snapshot.json> [out.json]
Lets tl_frames.py and diff_edits.py work from the source files and real names without touching the app's playhead."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, main_track

if len(sys.argv) < 2:
    sys.exit(__doc__)
snap = json.load(open(sys.argv[1]))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'video-edit-copilot', 'clipmap.json')
m = json.load(open(out)) if os.path.exists(out) else {}
n = 0
for e in main_track({e['id']: e for e in snap['elements']}):
    if e['id'] in m:
        continue
    r = call('clipMetadata', id=e['id'])
    m[e['id']] = {'path': r.get('path'), 'name': r.get('name'), 'captured': r.get('captured'), 'dur': r.get('duration'),
                  'w': (r.get('video') or {}).get('width'), 'h': (r.get('video') or {}).get('height')}
    n += 1
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
json.dump(m, open(out, 'w'), indent=0)
print(f'{n} new, {len(m)} total -> {out}')
