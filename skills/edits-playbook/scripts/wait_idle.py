"""Wait until the user has left the app alone: exits once the playhead, playing state and project title have been
unchanged (and not playing) for <secs> seconds (default 90). Run it in the background before making changes.
  python3 -I wait_idle.py [secs] [max_minutes]"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call

need = float(sys.argv[1]) if len(sys.argv) > 1 else 90
stop = time.time() + 60 * (float(sys.argv[2]) if len(sys.argv) > 2 else 120)
last, since = None, time.time()
while time.time() < stop:
    try:
        s = call('state')
        cur = (s.get('isPlaying'), round(s.get('currentTime') or 0, 2), s.get('projectTitle'))
    except Exception as e:
        cur = ('err', str(e)[:40])
    if cur != last:
        last, since = cur, time.time()
    elif time.time() - since >= need and not cur[0]:
        print('idle for', int(time.time() - since), 's at', cur)
        sys.exit(0)
    time.sleep(5)
print('gave up waiting; last state', last)
sys.exit(1)
