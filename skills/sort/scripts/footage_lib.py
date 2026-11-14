"""Shared helpers for footage_map.py and sort_footage.py: find media, read when each clip was shot, probe it.
Read-only. Never changes a file."""
import os, re, json, subprocess, datetime

VIDEO = {'.mp4', '.mov', '.m4v', '.mts', '.m2ts', '.avi', '.mkv'}
PHOTO = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.dng'}
SKIP_DIRS = {'.Spotlight-V100', '.Trashes', '.fseventsd', '.TemporaryItems'}
DAY_STARTS_AT = 4          # shots before 04:00 count as the previous day (late nights stay with their day)

_STAMP = re.compile(r'(20\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_ T]?(\d{2})[-_.]?(\d{2})[-_.]?(\d{2})')


def media_files(root):
    """Every video and photo under root, sorted by path. Skips hidden files, macOS resource forks and system folders."""
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if not x.startswith('.') and x not in SKIP_DIRS)
        for f in sorted(files):
            if f.startswith('.'):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in VIDEO or ext in PHOTO:
                out.append(os.path.join(d, f))
    return out


def kind(path):
    return 'video' if os.path.splitext(path)[1].lower() in VIDEO else 'photo'


def probe(path):
    """Duration, size, frame rate and creation tags via ffprobe ({} if it can't read the file)."""
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', path],
                           capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or '{}')
    except Exception:
        return {}
    v = next((s for s in d.get('streams', []) if s.get('codec_type') == 'video'), {})
    tags = {**(d.get('format', {}).get('tags') or {}), **(v.get('tags') or {})}
    w, h = v.get('width'), v.get('height')
    rot = 0
    for sd in v.get('side_data_list') or []:
        if 'rotation' in sd:
            rot = abs(int(float(sd['rotation'])))
    if rot in (90, 270) and w and h:
        w, h = h, w
    fr = v.get('avg_frame_rate') or '0/1'
    try:
        n, dd = fr.split('/'); fps = round(float(n) / float(dd), 3) if float(dd) else 0
    except Exception:
        fps = 0
    return {'duration': float(d.get('format', {}).get('duration') or 0), 'width': w, 'height': h, 'fps': fps,
            'codec': v.get('codec_name'), 'pix_fmt': v.get('pix_fmt'), 'transfer': v.get('color_transfer'),
            'primaries': v.get('color_primaries'), 'tags': tags}


def camera(info):
    """The camera model the file names, if any (e.g. 'DJI OsmoPocket3', 'Apple iPhone 16 Pro Max')."""
    t = (info or {}).get('tags') or {}
    model = t.get('com.apple.quicktime.model') or t.get('model')
    if model:
        make = t.get('com.apple.quicktime.make') or t.get('make') or ''
        return f'{make} {model}'.strip()
    enc = t.get('encoder') or ''
    return enc if enc and not enc.lower().startswith(('lavf', 'lavc', 'handbrake')) else ''


def shot_time(path, info=None):
    """(datetime, source) for when the clip was shot. Prefers a timestamp in the file name (camera local time), then the
    phone's local creation date tag, then the UTC creation_time converted to this computer's time zone, then the
    file's modified time (flagged as unreliable)."""
    m = _STAMP.search(os.path.basename(path))
    if m:
        try:
            return datetime.datetime(*map(int, m.groups())), 'file name'
        except ValueError:
            pass
    tags = (info or {}).get('tags') or {}
    t = tags.get('com.apple.quicktime.creationdate')
    if t:
        try:
            return datetime.datetime.fromisoformat(t.replace('Z', '+00:00')).replace(tzinfo=None), 'phone date tag'
        except ValueError:
            pass
    t = tags.get('creation_time')
    if t:
        try:
            utc = datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
            return utc.astimezone().replace(tzinfo=None), 'creation_time (UTC, shown in this computer\'s time zone)'
        except ValueError:
            pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)), 'file modified time (unreliable)'


def trip_day(dt):
    """The calendar day a shot belongs to, with late-night shots kept on the day before."""
    return (dt - datetime.timedelta(hours=DAY_STARTS_AT)).date()


def settings():
    p = os.path.join(os.getcwd(), 'video-edit-copilot', 'settings.json')
    try:
        return json.load(open(p))
    except Exception:
        return {}


def fmt_dur(s):
    s = int(round(s or 0))
    return f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}' if s >= 3600 else f'{s // 60}:{s % 60:02d}'
