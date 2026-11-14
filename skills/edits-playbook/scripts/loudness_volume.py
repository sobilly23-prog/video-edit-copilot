"""Measure a clip range's loudness and suggest the clip volume that evens out quick cuts.
  python3 -I loudness_volume.py <file> <in_s> <out_s> [--target -21] [--base 0.3] [--divisor 20] [--cap 2.0]
volume = base x 10^((target - LUFS) / divisor). Divisor 20 is a full loudness match (lively montages); 40 is a
gentle half-strength match (calm sections). Base: 1.0 when the clips' own sound carries the film (a first cut with no
music); about 0.3 when music plays on top (the default here). A near-silent shot can't be lifted without hiss: raise the music there.
No app connection needed: it reads the source file with ffmpeg."""
import sys, re, subprocess

a = sys.argv[1:]


def opt(name, default):
    return float(a[a.index(name) + 1]) if name in a else default


if len(a) < 3:
    sys.exit(__doc__)
f, t0, t1 = a[0], float(a[1]), float(a[2])
target, base, div, cap = opt('--target', -21.0), opt('--base', 0.3), opt('--divisor', 20.0), opt('--cap', 2.0)
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', f,
                    '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
if not m:
    sys.exit('no loudness reading (no audio track?)')
lufs = float(m[-1])
vol = min(cap, base * 10 ** ((target - lufs) / div))
print(f'{lufs:.1f} LUFS -> volume {vol:.3f}')
