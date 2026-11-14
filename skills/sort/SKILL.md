---
name: sort
description: Sorts and maps the user's footage. Builds a one-page footage map (frames from every clip, log colour converted once a LUT is set) and, if the footage isn't sorted yet, proposes a chronological layout (place from an itinerary, then day, then category and place, with review folders for travel days and stray dates) that moves files only after the user approves it, with a full undo. Use when the user runs /video-edit-copilot:sort, asks to organise or see their footage, or setup finds an unsorted folder.
---

# Sort and see the footage

Sorted footage makes everything after it faster: scenes are obvious, place names come from folder names, and finding
"that shot of the noodles" takes seconds. Seeing it all on one page is the fastest way for the user (and you) to find
the story before cutting anything.

**Chronological is the default:** by date and place, in the order it was lived. It suits travel and most personal
videos. If the user wants another structure (a wedding by part of the day, a product video by topic), offer to research
how people usually organise that kind of video, and propose that instead.

## 1. See it: the footage map (read-only)

```
python3 -I <this skill's folder>/scripts/footage_map.py <footage folder> <out.html> [--workers 2]
```
- One strip of frames per clip, grouped by folder, folders in the order they were shot, with the time, length and size
  of each clip. A dashed line marks a 20+ minute gap, which usually means a new place.
- Log clips are converted with `log_lut` and `log_sources` from `video-edit-copilot/settings.json` (or `--lut` and
  `--log-pattern`), so the colours are real. Before a LUT is chosen, frames are shown as shot.
- It also writes `<out>.json`, the clip index (path, when it was shot and how that was worked out, length, size, log).
- About 2 s per 4K clip, and it uses every CPU core. Use `--workers 2` while the user's video app is open. Run it in
  the background for hundreds of clips and say roughly how long it'll take.
- **Size:** about 35 KB per clip, so roughly 400 clips per page fits a 16 MB published page. For more, make one map per
  day, or use `--frames 3 --h 72`.
- Publish the page if this session can (for example as a Claude artifact). Otherwise open the file. Images are
  embedded, so it's a single file.

## 2. Propose a sort (read-only)

Only if the footage isn't already sorted the way the user likes. Ask before proposing a new layout for footage they've
already organised.

### Ask for the itinerary
Any form works: notes, a doc, a calendar, booking emails, a list in chat. Turn it into `itinerary.json`:
```json
{"places": [{"name": "Lisbon", "from": "2026-05-01", "to": "2026-05-04"},
            {"name": "Porto",  "from": "2026-05-04", "to": "2026-05-07"}]}
```
- Dates are inclusive. A travel day appears in both places, and its clips go to a review folder, because the date
  alone can't say which place they belong to.
- Without an itinerary, the layout is one folder per day.

### Suggest the categories
The default travel categories are `01_Food`, `02_Coffee-Shops`, `03_B-Roll` and `04_Sights-and-Places`. Tell the user
these are the defaults, and that they can add, rename or drop any (for example `05_Hotels` or `06_Night-Out`). Use
`--categories` with their list, or `--no-categories`.

### Make the plan
```
python3 -I <this skill's folder>/scripts/sort_footage.py propose <footage folder> <plan.json> \
    [--itinerary itinerary.json] [--categories "01_Food,02_Coffee-Shops,03_B-Roll,04_Sights-and-Places"] [--gap 20]
```
With an itinerary, the proposed layout is:
```
_00_Inbox-Unsorted/                      for anything added later
_01_Transfer-Day-Review/<date>/          travel days, to be assigned by hand
_02_Out-of-Range-Review/<date>/          clips dated outside the itinerary (kept, never discarded)
01_<Place>/<date>/01_Food/ 02_Coffee-Shops/ 03_B-Roll/ 04_Sights-and-Places/
01_<Place>/<date>/<NN scene HHMM>/<clip>  until you name the scenes
```
- **When each clip was shot** comes from the file name (camera time) first, then a phone's local date tag, then the
  file's creation time.
  - Files with none of those are dated by their modified time and flagged. Check those by eye.
  - **Never use Finder dates:** they're shifted to the computer's time zone and can put morning clips on the day
    before.
  - Camera and phone clocks often disagree, and a camera set to home time puts a whole trip hours off. Say so if the
    days look wrong.
- Shots after midnight stay with the day before, until 04:00.
- Never change a file name, only its folder.

## 3. Name the scenes

Look at the footage map and move each scene in the plan into its category and place. For example, change
`01_Lisbon/2026-05-02/03 scene 1412/` to `01_Lisbon/2026-05-02/01_Food/Time Out Market/`.
- Look names and spellings up on a map or the place's own site rather than guessing. Signs in the frames help.
- Anything you can't identify keeps its scene name, marked for the user to check.

## 4. Get approval, then apply

1. Run `sort_footage.py check <plan.json>`. It validates the plan (missing files, clashes, anything outside the footage
   folder) and prints a folder-by-folder summary. Show that summary to the user.
2. **Apply only after a clear yes.** Moving someone's original footage is the one time this plugin touches source
   files, so it needs their explicit approval of this exact plan.
   ```
   python3 -I <this skill's folder>/scripts/sort_footage.py apply <plan.json> --yes
   ```
   It moves files inside the footage folder only, never overwrites, creates the empty category and inbox folders, and
   logs every change in `<plan>.undo.json` as it goes.
3. If they'd rather not move anything, copy instead: `apply <plan.json> --yes --copy-to <new folder>`. That needs as
   much free space as the footage. It's also the way to sort straight off a memory card: leave the card read-only and
   copy only the video files.
4. To put everything back: `sort_footage.py undo <plan>.undo.json`.

After a sort, paths in the app's project (if one exists) may break. Sort before importing anything into the app, or
relink afterwards with the user's OK.

## 5. Hand over

Tell them:
- how many places, days and scenes there are
- what went to the review folders
- what's still unnamed or uncertain
- where the undo file is

Then go on to `first-cut`.

## Done when

- The footage map exists, and it's published or open for the user.
- If a sort was approved: `check` reported no problems before `apply`, every file is where the plan says, and the undo
  file's location has been given to the user.
- No file was renamed, overwritten or moved outside the footage folder.
