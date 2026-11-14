"""Build a caption picks page from a questions file (see ../SKILL.md for the format).
  python3 -I make_picks.py <questions.json> <out.html>
Image paths in the questions file are relative to the questions file. Images are embedded as data: URIs
(keep them about 640 px wide)."""
import sys, os, json, base64, html

if len(sys.argv) < 3:
    sys.exit(__doc__)
src_path = os.path.abspath(sys.argv[1])
src = json.load(open(src_path))
base = os.path.dirname(src_path)
qs = []
for q in src['questions']:
    q = dict(q)
    p = q['img'] if os.path.isabs(q['img']) else os.path.join(base, q['img'])
    mime = 'image/png' if p.lower().endswith('.png') else 'image/jpeg'
    with open(p, 'rb') as f:
        q['img'] = f'data:{mime};base64,' + base64.b64encode(f.read()).decode()
    q.setdefault('links', [])
    q.setdefault('note', '')
    q.setdefault('alt', q.get('title', ''))
    qs.append(q)
t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'picks_template.html')).read()
data = json.dumps(qs, ensure_ascii=False).replace('</', '<\\/')
t = (t.replace('/*DATA*/', data).replace('/*TITLE*/', html.escape(src['title'])).replace('/*H1*/', html.escape(src['h1']))
      .replace('/*INTRO*/', html.escape(src['intro'])).replace('/*KEY*/', src['key']).replace('/*LABEL*/', src['label']))
open(sys.argv[2], 'w').write(t)
print('wrote', sys.argv[2], len(t) // 1024, 'KB,', len(qs), 'questions')
