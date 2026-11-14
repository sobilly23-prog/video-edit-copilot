"""READ-ONLY snapshot of the open Edits project: every element, transition and clip, with exact timings.
  python3 -I snapshot.py <out.json> ["expected project title"]
Pass the expected title, exactly as the app shows it: it refuses to write if a different project is open. Take one before handing a cut over and
one after the user's review; diff_edits.py compares them."""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, paged, same_title

if len(sys.argv) < 2:
    sys.exit(__doc__)
st = call('state')
if len(sys.argv) > 2 and not same_title(sys.argv[2], st.get('projectTitle')):
    sys.exit(f"open project is {st.get('projectTitle')!r}, expected {sys.argv[2]!r}: not writing {sys.argv[1]}")
tr = call('transitions')
snap = {
    'taken': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    'project': st.get('projectTitle') or st.get('title'),
    'duration': st.get('duration'),
    'elements': paged('elements', 'elements'),
    'transitions': tr.get('transitions', tr) if isinstance(tr, dict) else tr,
    'clips': paged('clips', 'clips'),
}
os.makedirs(os.path.dirname(os.path.abspath(sys.argv[1])), exist_ok=True)
json.dump(snap, open(sys.argv[1], 'w'), indent=1)
print(f"{snap['project']!r}: {snap['duration']:.1f}s, {len(snap['elements'])} elements, "
      f"{len(snap['clips'])} clips, {len(snap['transitions'])} transitions -> {sys.argv[1]}")
