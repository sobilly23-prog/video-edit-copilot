"""Sort a footage folder chronologically: by place (from an itinerary), then day, then scene, safely.
  python3 -I sort_footage.py propose <footage folder> <plan.json> [--itinerary itinerary.json] [--gap 20]
                                     [--categories "01_Food,02_Coffee-Shops,03_B-Roll,04_Sights-and-Places"]
                                     [--no-categories]
      READ-ONLY. Writes a plan: every file's current path and proposed path. A new scene starts after a gap of --gap
      minutes. File names are never changed.
      Without an itinerary:  <day>/<NN scene HHMM>/<file>
      With one:              <NN_Place>/<day>/<NN scene HHMM>/<file>, plus
                             _00_Inbox-Unsorted/                 for anything added later
                             _01_Transfer-Day-Review/<day>/...   days that belong to two places
                             _02_Out-of-Range-Review/<day>/...   days outside the itinerary
      itinerary.json: {"places": [{"name": "Lisbon", "from": "2026-05-01", "to": "2026-05-04"}, ...]} (dates
      inclusive; a shared day such as a travel day appears in two places).
      Categories: empty folders created in every day folder (default: the four travel ones above; --no-categories
      for none). Then rename each scene in the plan into its category and place, e.g.
      "01_Lisbon/2026-05-02/01_Food/Time Out Market/<file>", before applying.
  python3 -I sort_footage.py check <plan.json>
      READ-ONLY. Validates the plan and prints a summary, so the user can approve it.
  python3 -I sort_footage.py apply <plan.json> --yes [--copy-to <folder>]
      Moves the files as planned, inside the footage folder only, and records every move in <plan>.undo.json as it
      goes. With --copy-to, copies into a new folder instead and leaves the originals where they are.
      Only run this after the user has approved the plan.
  python3 -I sort_footage.py undo <plan.undo.json>
      Moves every file back, newest move first, and removes the folders the sort created if they're empty.
Never deletes or renames a file, never overwrites one, and never moves anything outside the footage folder."""
import sys, os, json, shutil, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from footage_lib import media_files, kind, probe, shot_time, trip_day

a = sys.argv[1:]
if not a:
    sys.exit(__doc__)
cmd = a.pop(0)


def opt(name, default=None, cast=str):
    if name in a:
        i = a.index(name); v = cast(a[i + 1]); del a[i:i + 2]; return v
    return default


def inside(root, p):
    root, p = os.path.realpath(root), os.path.realpath(p)
    return p == root or p.startswith(root + os.sep)


def load_checked(path):
    plan = json.load(open(path))
    root = plan['root']
    seen, problems = set(), []
    for m in plan['moves']:
        src, dst = os.path.join(root, m['from']), os.path.join(root, m['to'])
        if os.path.basename(m['from']) != os.path.basename(m['to']):
            problems.append(f'renames a file: {m["from"]} -> {m["to"]}')
        if not os.path.exists(src):
            problems.append(f'missing: {m["from"]}')
        if not inside(root, src) or not inside(root, dst):
            problems.append(f'outside the footage folder: {m["from"]} -> {m["to"]}')
        if m['to'] in seen:
            problems.append(f'two files planned for {m["to"]}')
        seen.add(m['to'])
        if m['from'] != m['to'] and os.path.exists(dst):
            problems.append(f'already exists, would overwrite: {m["to"]}')
    for d in plan.get('make_dirs', []):
        if not inside(root, os.path.join(root, d)):
            problems.append(f'folder outside the footage folder: {d}')
    return plan, problems


DEFAULT_CATEGORIES = '01_Food,02_Coffee-Shops,03_B-Roll,04_Sights-and-Places'


def safe_name(n):
    return ''.join(c if c not in '/:\\' else '-' for c in n).strip()


if cmd == 'propose':
    gap = opt('--gap', 20, float)
    itin_path = opt('--itinerary')
    cats = opt('--categories', DEFAULT_CATEGORIES)
    if '--no-categories' in a:
        a.remove('--no-categories'); cats = ''
    cats = [c.strip() for c in cats.split(',') if c.strip()]
    places = []
    if itin_path:
        for i, pl in enumerate(json.load(open(itin_path))['places'], 1):
            places.append((f'{i:02d}_{safe_name(pl["name"])}', datetime.date.fromisoformat(pl['from']),
                           datetime.date.fromisoformat(pl['to'])))
    root, out = os.path.abspath(a[0]), a[1]

    def day_folder(d):
        """Where a day's clips go: its place, a review folder for shared days, or out of range."""
        if not places:
            return d.isoformat()
        hits = [name for name, f, t in places if f <= d <= t]
        if len(hits) == 1:
            return f'{hits[0]}/{d.isoformat()}'
        if len(hits) > 1:
            return f'_01_Transfer-Day-Review/{d.isoformat()}'
        return f'_02_Out-of-Range-Review/{d.isoformat()}'
    items = []
    for p in media_files(root):
        info = probe(p) if kind(p) == 'video' else {}
        dt, src = shot_time(p, info)
        items.append((dt, p, src))
    items.sort()
    moves, scene, prev, day, unreliable = [], 0, None, None, 0
    for dt, p, src in items:
        d = trip_day(dt)
        if d != day:
            day, scene, prev = d, 0, None
        if prev is None or (dt - prev).total_seconds() > gap * 60:
            scene += 1
            folder = f'{day_folder(d)}/{scene:02d} scene {dt:%H%M}'
        prev = dt
        unreliable += 'unreliable' in src
        moves.append({'from': os.path.relpath(p, root), 'to': f'{folder}/{os.path.basename(p)}',
                      'shot': dt.isoformat(timespec='seconds'), 'time_source': src})
    day_dirs = sorted({m['to'].rsplit('/', 2)[0] for m in moves})
    make_dirs = []
    if places:
        make_dirs.append('_00_Inbox-Unsorted')
    for dd in day_dirs:
        if not dd.startswith(('_01_', '_02_')):
            make_dirs += [f'{dd}/{c}' for c in cats]
    json.dump({'root': root, 'created': datetime.datetime.now().isoformat(timespec='seconds'),
               'note': 'Move each scene into its category and place (keep the place and day folders), then run check, '
                       'then apply after approval.',
               'categories': cats, 'make_dirs': make_dirs, 'moves': moves}, open(out, 'w'), indent=1)
    review = sum(1 for m in moves if m['to'].startswith(('_01_', '_02_')))
    print(f'{len(moves)} files -> {len(day_dirs)} day folders, {len({m["to"].rsplit("/", 1)[0] for m in moves})} '
          f'scenes, {len(make_dirs)} empty folders to create. Plan: {out}')
    if review:
        print(f'{review} files are on shared or out-of-range days: they go to the review folders')
    if unreliable:
        print(f'warning: {unreliable} files have no shooting time in their name or tags; their day is a guess')

elif cmd == 'check':
    plan, problems = load_checked(a[0])
    folders = {}
    for m in plan['moves']:
        folders.setdefault(m['to'].rsplit('/', 1)[0], 0)
        folders[m['to'].rsplit('/', 1)[0]] += 1
    for f, n in sorted(folders.items()):
        print(f'{n:4d}  {f}')
    moving = sum(m['from'] != m['to'] for m in plan['moves'])
    empty = [d for d in plan.get('make_dirs', []) if d not in folders]
    if empty:
        print(f'{len(empty)} empty folders to create (categories and inbox), e.g. {empty[0]}')
    print(f'{moving} of {len(plan["moves"])} files would move.')
    print('\n'.join(['PROBLEMS:'] + problems) if problems else 'No problems found.')
    sys.exit(1 if problems else 0)

elif cmd == 'apply':
    copy_to = opt('--copy-to')
    if '--yes' not in a:
        sys.exit('Refusing: add --yes, and only after the user has approved the plan (run "check" first).')
    a.remove('--yes')
    plan, problems = load_checked(a[0])
    if problems:
        sys.exit('Not applied. Fix the plan first:\n' + '\n'.join(problems))
    root = plan['root']
    if copy_to:
        copy_to = os.path.abspath(copy_to)
        if inside(root, copy_to):
            sys.exit('--copy-to must be outside the footage folder')
        for m in plan['moves']:
            dst = os.path.join(copy_to, m['to'])
            if os.path.exists(dst):
                sys.exit(f'already exists: {dst}')
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(root, m['from']), dst)
        for d in plan.get('make_dirs', []):
            os.makedirs(os.path.join(copy_to, d), exist_ok=True)
        print(f'copied {len(plan["moves"])} files into {copy_to}; the originals are untouched')
        sys.exit(0)
    undo_path = os.path.splitext(a[0])[0] + '.undo.json'
    if os.path.exists(undo_path):
        sys.exit(f'{undo_path} exists: this plan was applied before. Undo it first, or start a new plan.')
    log = {'root': root, 'applied': datetime.datetime.now().isoformat(timespec='seconds'), 'created_dirs': [], 'done': []}

    def make_tree(d):
        new_dirs = []
        while not os.path.exists(d):
            new_dirs.append(d); d = os.path.dirname(d)
        for nd in reversed(new_dirs):
            os.mkdir(nd); log['created_dirs'].append(os.path.relpath(nd, root))

    for m in plan['moves']:
        if m['from'] == m['to']:
            continue
        src, dst = os.path.join(root, m['from']), os.path.join(root, m['to'])
        make_tree(os.path.dirname(dst))
        os.rename(src, dst)                                    # same folder tree, so this is a move, never a copy
        log['done'].append({'from': m['from'], 'to': m['to']})
        json.dump(log, open(undo_path, 'w'), indent=1)         # written after every move, so undo always matches
    for d in plan.get('make_dirs', []):
        make_tree(os.path.join(root, d))
    json.dump(log, open(undo_path, 'w'), indent=1)
    print(f'moved {len(log["done"])} files. To put everything back: sort_footage.py undo "{undo_path}"')

elif cmd == 'undo':
    log = json.load(open(a[0]))
    root, back = log['root'], 0
    for m in reversed(log['done']):
        src, dst = os.path.join(root, m['to']), os.path.join(root, m['from'])
        if not os.path.exists(src):
            print(f'skipped (no longer at {m["to"]})'); continue
        if os.path.exists(dst):
            print(f'skipped (something is already at {m["from"]})'); continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst); back += 1
    removed = 0
    for d in sorted(log['created_dirs'], key=len, reverse=True):
        p = os.path.join(root, d)
        try:
            if os.path.isdir(p) and not [f for f in os.listdir(p) if f != '.DS_Store']:
                shutil.rmtree(p) if os.listdir(p) else os.rmdir(p); removed += 1
        except OSError:
            pass
    os.rename(a[0], a[0] + '.undone')
    print(f'moved {back} files back and removed {removed} empty folders')

else:
    sys.exit(__doc__)
