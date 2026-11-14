"""Tiny client for Instagram Edits' local MCP server, shared by the playbook scripts.

It finds the server's URL and auth header in your own Claude Code config (~/.claude.json) by server name, so nothing
secret lives in the plugin and the token is never printed. The name comes from, in order:
  the VEC_MCP_SERVER environment variable,
  "mcp_server" in video-edit-copilot/settings.json (in the folder you run the script from),
  or "metapilot-native" (the name Edits' own `claude mcp add` command uses).

Run scripts from your project folder with `python3 -I <script>`; each script adds its own folder to the import path."""
import json, os, sys, base64, urllib.request, urllib.error


def settings():
    p = os.path.join(os.getcwd(), 'video-edit-copilot', 'settings.json')
    try:
        return json.load(open(p))
    except Exception:
        return {}


def _server():
    name = os.environ.get('VEC_MCP_SERVER') or settings().get('mcp_server') or 'metapilot-native'
    cfg = json.load(open(os.path.expanduser('~/.claude.json')))
    found = (cfg.get('mcpServers') or {}).get(name)
    if not found:
        for proj in (cfg.get('projects') or {}).values():
            found = (proj.get('mcpServers') or {}).get(name)
            if found:
                break
    if not found or not found.get('url'):
        sys.exit(f'No HTTP MCP server named {name!r} in ~/.claude.json. Connect the app first (see the setup skill).')
    return found['url'], dict(found.get('headers') or {})


_CONN = None


def _rpc(tool, args, timeout=300):
    global _CONN
    if _CONN is None:
        _CONN = _server()
    url, headers = _CONN
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                       'params': {'name': tool, 'arguments': args}}).encode()
    req = urllib.request.Request(url, body, {'Content-Type': 'application/json', 'Accept': 'application/json', **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
    except urllib.error.URLError as e:
        sys.exit(f'Could not reach the app ({e.reason}). Is it open, with its automation server enabled?')
    if raw.lstrip().startswith(('event:', 'data:')):          # some servers answer as server-sent events
        raw = [l[5:].strip() for l in raw.splitlines() if l.startswith('data:')][-1]
    d = json.loads(raw)
    if 'error' in d:
        raise RuntimeError(f'{tool} failed: {d["error"]}')
    return d.get('result', d)


def call(tool, **args):
    """Call a tool and return its JSON result (raises if the app reports ok: false)."""
    res = _rpc(tool, args)
    txt = ''.join(c.get('text', '') for c in res.get('content', []) if isinstance(c, dict))
    try:
        out = json.loads(txt)
    except Exception:
        out = {'raw': txt}
    if isinstance(out, dict) and out.get('ok') is False:
        raise RuntimeError(f'{tool} failed: {out}')
    return out


def image(tool, **args):
    """Call a tool that returns an image (e.g. captureFrame) and return the image bytes."""
    res = _rpc(tool, args, timeout=180)
    for c in res.get('content', []):
        if isinstance(c, dict) and (c.get('type') == 'image' or 'data' in c):
            return base64.b64decode(c['data'])
    raise RuntimeError(f'{tool} returned no image')


def paged(tool, key, size=200):
    out, off = [], 0
    while True:
        r = call(tool, limit=size, offset=off)
        out += r.get(key, [])
        if r.get('nextOffset') is None:
            return out
        off = r['nextOffset']


def elements():
    """Every element in the open project, by id."""
    return {e['id']: e for e in paged('elements', 'elements')}


def main_track(els):
    """The main video track's clips in time order (the track holding the most video clips)."""
    tracks = {}
    for e in els.values():
        if e.get('content') == 'video':
            tracks.setdefault(e['trackId'], []).append(e)
    if not tracks:
        return []
    return sorted(max(tracks.values(), key=len), key=lambda e: e['startTime'])


def same_title(a, b):
    """Exact match after trimming spaces. Never a substring: "Lisbon" must not match "Lisbon trip 2025"."""
    return (a or '').strip() == (b or '').strip()


def guard(title):
    """Stop unless the open project's title is exactly `title` (the user may have switched projects in the app)."""
    t = call('state').get('projectTitle') or ''
    if not title or not same_title(title, t):
        sys.exit(f'open project is {t!r}, expected exactly {title!r}: stopped')
    return t


def src_in(e):
    return e.get('sourceInPoint', e.get('sourceStart', 0)) or 0
