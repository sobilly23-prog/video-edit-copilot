"""Build YouTube thumbnail variants (1280x720) from your own graded frames, as HTML, and render them to JPG.
  python3 -I make_thumbnails.py <spec.json> <out_dir> [--no-render] [--chrome <path to Chrome or Chromium>]
Writes <key>.html for every variant (images embedded) and, unless --no-render, renders each with headless Chrome at 2x
and scales it to <key>.jpg (1280x720, under YouTube's 2 MB limit), plus preview_feed.jpg: every variant at phone-feed
size (168 px wide) and at 360 px, side by side, to check the title still reads when it's small.

spec.json (image paths are relative to the spec file):
{"style": {"font": "Instrument Serif",        a Google Fonts family for the title (match the film's title card)
           "italic": true, "weight": 400,
           "color": "#FFFFFF",                  title colour
           "sub_font": "Avenir Next, Helvetica Neue, Arial, sans-serif"},
 "variants": [{"key": "A_single_shot",
   "panels": [{"src": "frames/cafe.jpg", "x": 50, "y": 50, "zoom": 1.0, "flex": 1}],   1 panel = a single shot,
                                                  3 = the tall-panel triptych; x/y = which part of the image stays in view (%)
   "title": "Lisbon", "title_y": 150, "title_x": 640, "size": 190,    px on the 1280x720 canvas (centre of the word)
   "sub": "5 DAYS OF FOOD & COFFEE", "sub_size": 24,                  a line under the title (optional)
   "kicker": "", "kicker_size": 40, "kicker_font": "serif"|"sans",    a small line above the title (optional)
   "inset": {"src", "left", "top", "w", "h", "x", "y", "rotate", "radius", "border"},   optional photo card
   "gutter": 0, "gutter_color": "#000", "shade": 0.35}]}               shade = dark halo behind the title (0-1)
"""
import sys, os, json, html, base64, shutil, subprocess, mimetypes, tempfile

a = sys.argv[1:]


def opt(name, default=None):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return default


chrome = opt('--chrome')
render = '--no-render' not in a
if not render:
    a.remove('--no-render')
if len(a) != 2:
    sys.exit(__doc__)
spec_path, out = a
spec = json.load(open(spec_path))
base = os.path.dirname(os.path.abspath(spec_path))
os.makedirs(out, exist_ok=True)
st = {'font': 'Instrument Serif', 'italic': True, 'weight': 400, 'color': '#FFFFFF',
      'sub_font': 'Avenir Next, Helvetica Neue, Arial, sans-serif', **spec.get('style', {})}


def data_uri(src):
    p = src if os.path.isabs(src) else os.path.join(base, src)
    mt = mimetypes.guess_type(p)[0] or 'image/jpeg'
    return f'data:{mt};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


fam = st['font'].replace(' ', '+')
ital = 'ital,wght@1,%d' % st['weight'] if st['italic'] else 'wght@%d' % st['weight']
PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Thumbnail</title>
<link href="https://fonts.googleapis.com/css2?family={fam}:{ital}&display=block" rel="stylesheet">
<style>
html,body{{margin:0;padding:0;background:#000;width:1280px;height:720px;overflow:hidden}}
.c{{position:relative;width:1280px;height:720px;overflow:hidden;background:{gc};display:flex;gap:{g}px}}
.p{{position:relative;overflow:hidden;min-width:0}}
.p img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.shade{{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 600px 260px at {cx}px {sc}px, rgba(0,0,0,{sh}) 0%, rgba(0,0,0,{sh2}) 45%, rgba(0,0,0,0) 100%)}}
.t{{position:absolute;left:{lx}px;right:{rx}px;top:{ty}px;transform:translateY(-58%);text-align:center;
  font-family:'{font}',serif;font-style:{fstyle};font-weight:{fw};font-size:{fs}px;line-height:1;letter-spacing:-0.01em;
  color:{color};text-shadow:0 2px 4px rgba(0,0,0,.55),0 6px 28px rgba(0,0,0,.45)}}
.s,.k{{position:absolute;left:{lx}px;right:{rx}px;text-align:center;color:#fff;
  text-shadow:0 1px 3px rgba(0,0,0,.75),0 4px 18px rgba(0,0,0,.55)}}
.s{{top:{sy}px;font-family:{subf};font-weight:600;font-size:{ss}px;letter-spacing:.24em}}
.k{{top:{ky}px;{kfont}}}
.inset{{position:absolute;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.inset img{{width:100%;height:100%;object-fit:cover;display:block}}
</style></head><body><div class="c">{panels}<div class="shade"></div>{inset}{kicker}<div class="t">{title}</div>{sub}</div>
</body></html>"""

keys = []
for v in spec['variants']:
    ps = []
    for p in v['panels']:
        z = p.get('zoom', 1.0)
        tr = f'transform:scale({z});transform-origin:{p.get("x", 50)}% {p.get("y", 50)}%;' if z != 1 else ''
        ps.append(f'<div class="p" style="flex:{p.get("flex", 1)}"><img src="{data_uri(p["src"])}" '
                  f'style="object-position:{p.get("x", 50)}% {p.get("y", 50)}%;{tr}"></div>')
    ty, fs = v.get('title_y', 200), v.get('size', 200)
    sub, kicker, ks = v.get('sub', ''), v.get('kicker', ''), v.get('kicker_size', 40)
    kfont = (f"font-family:'{st['font']}',serif;font-style:{'italic' if st['italic'] else 'normal'};font-size:{ks}px"
             if v.get('kicker_font', 'serif') == 'serif' else
             f"font-family:{st['sub_font']};font-weight:600;letter-spacing:.24em;font-size:{ks}px")
    sh = v.get('shade', 0.35)
    ins = ''
    if v.get('inset'):
        i = v['inset']
        ins = (f'<div class="inset" style="left:{i["left"]}px;top:{i["top"]}px;width:{i["w"]}px;height:{i["h"]}px;'
               f'border:{i.get("border", 6)}px solid #fff;border-radius:{i.get("radius", 10)}px;'
               f'transform:rotate({i.get("rotate", 0)}deg)"><img src="{data_uri(i["src"])}" '
               f'style="object-position:{i.get("x", 50)}% {i.get("y", 50)}%"></div>')
    cx = v.get('title_x', 640)
    page = PAGE.format(fam=fam, ital=ital, font=st['font'], fstyle='italic' if st['italic'] else 'normal',
                       fw=st['weight'], color=st['color'], subf=st['sub_font'],
                       lx=cx - 640, rx=640 - cx, cx=cx, gc=v.get('gutter_color', '#000'), g=v.get('gutter', 0),
                       ty=ty, fs=fs, sh=sh, sh2=round(sh * 0.45, 3), sc=ty + (12 if sub else 0),
                       sy=ty + fs * 0.40 + v.get('sub_gap', 4), ss=v.get('sub_size', 22),
                       ky=ty - fs * 0.58 - ks * 0.9 + v.get('kicker_gap', 0), kfont=kfont,
                       panels=''.join(ps), inset=ins, title=html.escape(v.get('title', '')),
                       sub=f'<div class="s">{html.escape(sub)}</div>' if sub else '',
                       kicker=f'<div class="k">{html.escape(kicker)}</div>' if kicker else '')
    open(os.path.join(out, v['key'] + '.html'), 'w').write(page)
    keys.append(v['key'])
print('pages:', ', '.join(keys))
if not render:
    sys.exit(0)

CANDIDATES = [chrome, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              '/Applications/Chromium.app/Contents/MacOS/Chromium',
              '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
              shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')]
exe = next((c for c in CANDIDATES if c and os.path.exists(c)), None)
if not exe:
    sys.exit('No Chrome/Chromium found to render with. Open the .html files in a browser at 1280x720 and screenshot '
             'them, or pass --chrome <path>.')
tmp = tempfile.mkdtemp(prefix='thumbs_')
for k in keys:
    png = os.path.join(tmp, k + '.png')
    subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
                    '--window-size=1280,720', '--virtual-time-budget=15000', f'--user-data-dir={tmp}/profile',
                    f'--screenshot={png}', 'file://' + os.path.abspath(os.path.join(out, k + '.html'))],
                   capture_output=True, timeout=180)
    if not os.path.exists(png):
        sys.exit(f'Rendering {k} failed')
    jpg = os.path.join(out, k + '.jpg')
    for q in (2, 3, 4, 6):                                           # stay under YouTube's 2 MB thumbnail limit
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', png, '-vf', 'scale=1280:720:flags=lanczos',
                        '-q:v', str(q), jpg], check=True)
        if os.path.getsize(jpg) < 1.9e6:
            break
    print(f'{jpg}  {os.path.getsize(jpg) / 1e6:.2f} MB')
ins = sum([['-i', os.path.join(out, k + '.jpg')] for k in keys], [])
n = len(keys)
small = ''.join(f'[{i}:v]scale=168:-2,pad=188:105:10:5:white[s{i}];' for i in range(n))
mid = ''.join(f'[{i}:v]scale=360:-2,pad=380:213:10:6:white[m{i}];' for i in range(n))
row = lambda p: (''.join(f'[{p}{i}]' for i in range(n)) + (f'hstack=inputs={n}' if n > 1 else 'null') + f'[{p}]')
fc = (small + mid + row('s') + ';' + row('m') + ';[s]pad=iw*' + f'{380 / 188:.5f}' + ':ih:0:0:white[sp];' +
      '[sp][m]vstack=inputs=2[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-frames:v', '1',
                os.path.join(out, 'preview_feed.jpg')], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print('preview:', os.path.join(out, 'preview_feed.jpg'))
