"""Delete exactly one element by id, or nothing.
In Edits, selecting by id can fail silently, and `delete` then removes whatever happens to be selected (possibly the
user's work). This compares the element set before and after and undoes the delete if anything else went.
  python3 -I safe_delete.py "<project title>" <element id> [<element id> ...]
The title must match the open project exactly, or nothing is deleted."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edits_api import call, elements, guard


def safe_delete(eid):
    before = set(elements())
    if eid not in before:
        return 'absent'
    call('clearSelection')
    call('selectById', id=eid, addToSelection=False)
    call('delete')
    gone = before - set(elements())
    if gone == {eid}:
        call('clearSelection')
        return 'deleted'
    call('undo')
    call('clearSelection')
    raise RuntimeError(f'delete of {eid[:8]} removed {[g[:8] for g in gone]}; undone')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    guard(sys.argv[1])
    for e in sys.argv[2:]:
        print(e[:8], safe_delete(e))
