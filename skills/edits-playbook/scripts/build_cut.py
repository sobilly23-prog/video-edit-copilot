"""Build a cut from a plan into the OPEN Edits project: copy, import, trim, level and label every shot, then check it.
  python3 -I build_cut.py "<project title>" <plan.json> [--labels] [--level first|music|none] [--fade-out 3]
                          [--from N] [--no-copy] [--label-y 0.86] [--label-size 64]
plan.json:
  {"scenes": [{"label": "Night market", "shots": [{"file": "/path/to/clip.MP4", "in": 2.0, "out": 5.0}, ...]}, ...]}
- Copies each source file into "work_media" (video-edit-copilot/settings.json) unless it's already there. The
  originals are only read. --no-copy imports the paths as given (only if the app can read them).
- Appends each shot at the end of the timeline (Edits imports at the playhead), trims it, and checks its start, length
  and in-point. Stops at the first mismatch, so nothing piles up on a bad state. --from N resumes at shot N (1-based).
- --level first (default): volume from each range's loudness, matched to -21 LUFS at half strength with base 1.0, for
  a cut whose own sound carries it. music: base 0.3 (music will lead). none: leave clips at 1.0. Every clip gets
  2-frame audio fades.
- --labels: a working label on the first shot of each scene, 3 s from the cut: size 64, centred low, dark pill,
  opacity 0.85, fligFadeBox. For 9:16 short-form, use --label-y 0.35 --label-size 80 to keep text in the safe band
  (the first scene's label is the hook). Added after all the shots are in (Edits won't let text run past the end of the timeline),
  with the length set on creation (text trims are unreliable). A scene that already has its label is skipped.
- --fade-out N: dissolve to black at the end (stored N s; Edits shows about half) plus an audio fade on the last clip.
- Re-reads the main-track order and the film's length from the app, saves the project, and writes
  video-edit-copilot/build-log.json.
Only for a project made for this cut. Run wait_idle.py first if the user may be working in the app."""
import sys, os, re, json, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, guard, elements, main_track, settings

a = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


def flag(name):
    if name in a:
        a.remove(name); return True
    return False


labels, no_copy = flag('--labels'), flag('--no-copy')
level = opt('--level', 'first')
fade_out = opt('--fade-out', 0.0, float)
start_at = opt('--from', 1, int)
label_y = opt('--label-y', 0.86, float)
label_size = opt('--label-size', 64, float)
if len(a) != 2 or level not in ('first', 'music', 'none'):
    sys.exit(__doc__)
TITLE, plan = a[0], json.load(open(a[1]))
work = settings().get('work_media') or ''
if not no_copy and not work:
    sys.exit('Set "work_media" in video-edit-copilot/settings.json (a folder the app can read), or pass --no-copy.')

shots = [(sc.get('label') or '', i == 0, s) for sc in plan['scenes'] for i, s in enumerate(sc['shots'])]
if not shots:
    sys.exit('The plan has no shots.')


def lufs(path, t0, t1):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', path,
                        '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    return float(m[-1]) if m else None


def volume_for(path, t0, t1):
    if level == 'none':
        return 1.0, None
    L = lufs(path, t0, t1)
    if L is None or L < -60:
        return 1.0, L
    base = 1.0 if level == 'first' else 0.3
    return round(min(2.0, base * 10 ** ((-21 - L) / 40)), 3), L


def local_copy(src):
    if no_copy:
        return src
    if os.path.dirname(os.path.abspath(src)) == os.path.abspath(work):
        return src
    os.makedirs(work, exist_ok=True)
    dst = os.path.join(work, os.path.basename(src))
    if os.path.exists(dst):
        if os.path.getsize(dst) != os.path.getsize(src):
            sys.exit(f'{dst} exists with a different size: not overwriting. Rename one of them first.')
        return dst
    shutil.copy2(src, dst)
    return dst


def seek_end():
    d = call('state')['duration'] or 0
    for t in (d, d - 0.01, d + 0.01):
        call('seek', seconds=round(max(t, 0), 3))
        if abs((call('state').get('currentTime') or 0) - d) < 0.05:
            return d
    sys.exit(f'Could not put the playhead at the end ({d:.2f} s): stopped before importing.')


log_path = os.path.join('video-edit-copilot', 'build-log.json')
log = json.load(open(log_path)) if start_at > 1 and os.path.exists(log_path) else {'project': TITLE, 'shots': []}
for n, (label, first, s) in enumerate(shots, 1):
    if n < start_at:
        continue
    guard(TITLE)
    src = s['file'] if os.path.isabs(s['file']) else os.path.join(work, s['file'])
    path = local_copy(src)
    t_in, t_out = float(s['in']), float(s['out'])
    d = seek_end()
    eid = call('importMedia', path=path)['id']
    if t_in > 0:
        call('trim', id=eid, side='left', deltaSeconds=round(t_in, 4))
    e = elements()[eid]
    cut = e['sourceOutPoint'] - t_out
    if cut > 0.001:
        call('trim', id=eid, side='right', deltaSeconds=round(cut, 4))
    e = elements()[eid]
    vol, L = volume_for(path, t_in, t_out)
    call('setVolume', id=eid, volume=vol)
    call('setFade', id=eid, fadeIn=0.08, fadeOut=0.08)
    ok = (abs(e['startTime'] - d) < 0.06 and abs(e['duration'] - (t_out - t_in)) < 0.06
          and abs((e.get('sourceInPoint') or 0) - t_in) < 0.06)
    row = {'n': n, 'file': os.path.basename(path), 'id': eid, 'start': round(e['startTime'], 3),
           'length': round(e['duration'], 3), 'in': t_in, 'out': t_out, 'lufs': L, 'volume': vol, 'scene': label}
    print(row, flush=True)
    log['shots'].append(row)
    json.dump(log, open(log_path, 'w'), indent=1)
    if not ok:
        sys.exit(f'Shot {n} does not match the plan (see above). Fix it in the app, then resume with --from {n + 1}.')

guard(TITLE)
if labels:
    els = elements()
    texts = [e for e in els.values() if e.get('content') == 'text']
    for r in log['shots']:
        lab = r.get('scene')
        first_of_scene = r is next(x for x in log['shots'] if x.get('scene') == lab)
        if not lab or not first_of_scene:
            continue
        clip = els.get(r['id'])
        if not clip:
            continue
        cut = round(clip['startTime'], 3)
        if any((t.get('text') or '').strip() == lab and abs(t['startTime'] - cut) < 0.3 for t in texts):
            print(f'label {lab!r}: already there')
            continue
        tid = call('addText', text=lab, duration=3.0, atSeconds=cut)['id']
        if abs(elements()[tid]['startTime'] - cut) > 0.02:
            call('move', id=tid, toSeconds=cut)
        call('setTextPosition', id=tid, x=0.5, y=label_y)
        call('setTextStyle', id=tid, size=label_size)
        call('setEmphasis', id=tid, style='backgroundPill', color='#1A1A1A')
        call('setOpacity', id=tid, opacity=0.85)
        call('setTextAnimation', id=tid, animation='fligFadeBox')
        t = elements()[tid]
        r['label_id'] = tid
        good = abs(t['duration'] - 3.0) < 0.05 and abs(t['startTime'] - cut) < 0.05
        print(f"label {lab!r}: {t['startTime']:.2f} s for {t['duration']:.2f} s{'' if good else '  <-- CHECK: not on the cut for 3 s'}")
built = [r['id'] for r in log['shots']]
order = [e['id'] for e in main_track(elements())]
if fade_out > 0 and built:
    call('addTransition', fromId=built[-1], filterId='transition_dissolve', durationSeconds=fade_out)
    call('setFade', id=built[-1], fadeIn=0.08, fadeOut=round(fade_out / 2, 2))
call('saveProject')
st = call('state')
want = round(sum(r['out'] - r['in'] for r in log['shots']), 2)
print(f"order matches the plan: {order == built} | {len(built)} shots | length {st['duration']:.2f} s "
      f"(plan {want:.2f} s) | saved")
log.update({'order_ok': order == built, 'duration': st['duration']})
json.dump(log, open(log_path, 'w'), indent=1)
if order != built or abs(st['duration'] - want) > 0.1 * len(built):
    sys.exit('The app does not match the plan: re-read the timeline before going on.')
