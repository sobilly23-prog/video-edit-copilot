"""READ-ONLY caption check on the open Edits project (or a snapshot). Run after every build and every review.
  python3 -I caption_check.py [--snapshot file.json] [--from 0] [--snap 0.6]
Reports:
  OVERLAP  two captions on screen at once. A card's name + address, and a title with its subtitle, count as one unit:
           items that end together and start within 0.75 s of each other.
  SHORT    on screen less than max(3 s, characters / 15) for a single caption, or 3 s for a card or title unit.
  OFFCUT   starts up to --snap seconds after a cut (should start ON the cut).
  ALIGN    a single caption that isn't centre-aligned (only if the listing reports alignment; cards are left-aligned
           by design, so check those by eye).
Nothing is changed. Fix with the app, then run it again."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import main_track

a = sys.argv[1:]
if '--snapshot' in a:
    els = {e['id']: e for e in json.load(open(a[a.index('--snapshot') + 1]))['elements']}
else:
    from edits_api import elements
    els = elements()
t_from = float(a[a.index('--from') + 1]) if '--from' in a else 0.0
SNAP = float(a[a.index('--snap') + 1]) if '--snap' in a else 0.6

cuts = sorted({round(c['startTime'], 3) for c in main_track(els)})
texts = sorted([e for e in els.values() if e.get('content') == 'text' and e['startTime'] >= t_from],
               key=lambda e: (e['startTime'], e['endTime']))
units = []
for e in texts:
    u = units[-1] if units else None
    if u and abs(u['end'] - e['endTime']) < 0.05 and e['startTime'] - u['start'] <= 0.75:
        u['els'].append(e)
    else:
        units.append({'start': e['startTime'], 'end': e['endTime'], 'els': [e]})

problems = 0
for i, u in enumerate(units):
    txt = ' | '.join((e.get('text') or '').strip() for e in u['els'])
    # a card (name + address) or a title with its subtitle just needs 3 s; a single line needs time to be read
    need = 3.0 if len(u['els']) > 1 else max(3.0, len((u['els'][0].get('text') or '').strip()) / 15)
    dur = u['end'] - u['start']
    tag = f"{u['start']:8.2f}-{u['end']:8.2f}  {txt[:70]}"
    if i + 1 < len(units) and units[i + 1]['start'] < u['end'] - 0.02:
        print(f'OVERLAP  {tag}  <->  {units[i + 1]["start"]:.2f} {(units[i + 1]["els"][0].get("text") or "")[:40]}'); problems += 1
    if dur < need - 0.02:
        print(f'SHORT    {tag}  ({dur:.2f} s, needs {need:.2f})'); problems += 1
    after = [u['start'] - c for c in cuts if 0.02 < u['start'] - c <= SNAP]
    if after:
        print(f'OFFCUT   {tag}  (starts {min(after):.2f} s after a cut)'); problems += 1
    if len(u['els']) == 1 and u['els'][0].get('textAlignment') not in (None, 'center'):
        print(f"ALIGN    {tag}  ({u['els'][0].get('textAlignment')}; fine if it's a place card)")
print(f'{len(units)} caption units, {problems} problems')
