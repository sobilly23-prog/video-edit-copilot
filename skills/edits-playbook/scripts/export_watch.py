"""READ-ONLY. Watch an Edits export from start to finish and report progress, speed and problems.
  python3 -I export_watch.py [--wait-start 45] [--every 10] [--path "/Volumes/My Drive"]... [--no-caffeinate]
Waits up to --wait-start minutes for the user to start the export (it never starts one itself), then checks every
15 s and prints a line every --every minutes: progress, % per minute, minutes left. Exits when the export completes,
fails or is cancelled, printing a FINAL line with the app's last status. Run it in the background and read its output.
--path: a drive or folder the project reads media from. If it disappears mid-export, it prints PATH GONE right away
(the export will fail when it reaches a shot on it).
On macOS it keeps the display and the computer awake while it runs (caffeinate). With the display asleep, Edits'
export slowed to almost nothing in testing, so a 2-hour export took 4."""
import sys, os, time, datetime, platform, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


wait_start = opt('--wait-start', 45, float)
every = opt('--every', 10, float)
paths = []
while '--path' in a:
    paths.append(opt('--path'))
if platform.system() == 'Darwin' and '--no-caffeinate' not in a and shutil.which('caffeinate'):
    subprocess.Popen(['caffeinate', '-d', '-i', '-w', str(os.getpid())])
now = lambda: datetime.datetime.now().strftime('%H:%M')
ACTIVE = ('exporting', 'preparing')


def status():
    try:
        return call('exportStatus')
    except (Exception, SystemExit) as e:                # the app busy or briefly unreachable: try again next minute
        return {'state': 'unreachable', 'error': str(e)[:120]}


w0 = time.time()
while True:
    s = status()
    if s.get('state') in ACTIVE:
        print(now(), 'export started:', s.get('outputPath', ''), flush=True)
        break
    if time.time() - w0 > wait_start * 60:
        print(now(), f'NO EXPORT STARTED within {wait_start:.0f} min. Last status: {s}', flush=True)
        sys.exit(0)
    time.sleep(20)

t0, p0 = time.time(), s.get('progress', 0) or 0
out_path = s.get('outputPath') or ''
last_print, misses, gone, ever_moved = t0, 0, set(), False
while True:
    time.sleep(15)                                  # short exports can finish within a minute
    s = status()
    if s.get('state') == 'unreachable':
        misses += 1
        if misses >= 40:
            print(now(), 'GAVE UP: the app has not answered for 10 minutes', s, flush=True)
            sys.exit(1)
        continue
    misses = 0
    t = time.time()
    state = s.get('state')
    active = state in ACTIVE
    p = (s.get('progress', 0) or 0) if active or state == 'complete' else None
    if p is not None and p > p0:
        ever_moved = True
    rate = (p - p0) / ((t - t0) / 60) if p is not None and t > t0 else 0      # fraction per minute since the start
    left = (1 - p) / rate if p is not None and rate > 0 else -1
    for path in paths:
        if path not in gone and not os.path.exists(path):
            gone.add(path)
            print(now(), f'PATH GONE{f" at {p * 100:.1f}%" if p is not None else ""}: {path}', flush=True)
    if active and t - last_print >= every * 60:
        print(f'{now()} {p * 100:5.1f}%  {rate * 100:4.2f}%/min  ~{left:4.0f} min left  {state}', flush=True)
        last_print = t
    if not active:
        took = (t - t0) / 60
        size = os.path.getsize(out_path) if out_path and os.path.exists(out_path) else 0
        if state == 'complete':
            print('FINAL complete', s, f'(took {took:.0f} min)', flush=True)
            sys.exit(0)
        if state == 'idle' and size > 0:
            # Closing the project (or a new one opening) resets the app's status to idle. Judge by the file instead.
            print(f'FINAL the app reports idle, but the file exists ({size / 1e6:.0f} MB): {out_path}. Check it with '
                  f'ffprobe before calling it done. (took about {took:.0f} min)', flush=True)
            sys.exit(0)
        print('FINAL', s, f'(took {took:.0f} min; output file {"missing" if not size else f"{size} bytes"})', flush=True)
        sys.exit(1)
