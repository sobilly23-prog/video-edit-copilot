"""Save TRUE export frames (grade, captions, fades, effects) from the open Edits project as JPEGs.
  python3 -I capture_frames.py <out_dir> <t1> [t2 ...] [--width 1920] [--sheet name.jpg|path/to/sheet.jpg --cols 4]
Use it to verify a build before handing over. These frames carry the captions; for picks pages use tl_frames.py
(clean frames) instead, or the page draws each caption twice."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import image

args = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default


width = opt('--width', 1920, int)
sheet = opt('--sheet')
cols = opt('--cols', 4, int)
if len(args) < 2:
    sys.exit(__doc__)
out = args[0]
os.makedirs(out, exist_ok=True)
files = []
for t in map(float, args[1:]):
    p = os.path.join(out, f'f_{t:09.2f}.jpg')
    open(p, 'wb').write(image('captureFrame', atSeconds=t, maxWidth=width))
    files.append(p)
    print(p, flush=True)
if sheet and files:
    sheet_path = sheet if os.path.dirname(sheet) else os.path.join(out, sheet)   # a bare name goes next to the frames
    os.makedirs(os.path.dirname(os.path.abspath(sheet_path)), exist_ok=True)
    lst = os.path.join(out, '_sheet.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
    rows = (len(files) + cols - 1) // cols
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-vf', f'scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,tile={cols}x{rows}',
                    '-frames:v', '1', sheet_path], check=True)
    print('sheet', sheet_path)
