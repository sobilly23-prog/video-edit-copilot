# Edits gotchas

Found while building a long film in Instagram Edits for Mac over its MCP server. Each one cost time once. Versions
change, so re-check before relying on one, and add new ones here, not in the user's taste profile.

## Timeline and clips

- **`importMedia` inserts at the playhead,** not at the end. Seek first. A seek to an exact frame time is sometimes
  refused ("playhead did not reach"): nudge by 0.01 s and confirm with `state`.
- **After trimming a long import, the playhead can end up past the timeline's end,** and the next seek to the end is
  refused. Seek to the end minus 1 s first.
- **Edits can shuffle main-track clips after an insert.** Always re-read the order and compare it with the plan or the
  last snapshot.
- **What ripples:**
  - Main-track clips, captions and adjustment pieces that start after the edit point shift.
  - A full-length conversion layer stretches.
  - A layer piece that spans the edit point does **not** stretch.
  - **Music never moves.**
  - Lengthening a clip's left edge also shifts captions sitting inside that clip.
- **`replaceElementMedia`** keeps the element's length and resets the in-point to 0. Slip the clip back if needed. A
  longer file still keeps the old length: lengthen with a negative right trim.
- **Swapping media back to a file the project already holds fails** (a duplicate-media error). If the swap was the
  last change, `undo` reverts it cleanly. Diff a snapshot afterwards to confirm nothing else changed.
- **Don't relink media to a different copy** (for example from an external drive to a local one) without asking. Users
  often want to keep working from their drive.
- **The user's own edits in the app:**
  - A trim can leave a **1-frame sliver** (0.04 s) of a clip. Flag it; don't delete their piece.
  - An undo can quietly put back a clip's original media after you replaced it. Re-check replaced clips after their
    pass.
  - A ripple delete can move adjustment pieces onto other tracks, or over a phone clip.
- **`trim` sign:** a positive delta shortens that edge, a negative one lengthens it. Re-read after every trim.
- **Readbacks can lie:** a `move` reported success and didn't happen. Re-list and compare with the plan, and check
  `state.duration` against the expected film length.

## Colour

- Built-in LUT presets aren't always the camera maker's LUT, and can clip whites. See `colour-recipe.md`.
- Imported LUTs are kept for every project. Re-importing a file makes copies ("… 2", "… 3").
- `addAdjustmentLayer` needs `kind: "adjust"`.

## Selection and deleting

- `selectById` can fail silently, and `delete` then removes whatever is selected. That once deleted a song the user
  had placed. **Always delete through `safe_delete.py`.**

## Text

- `fadeIn` fades over the caption's whole length. Use a quick fade that holds.
- The pill colour's transparency is ignored. Lower the caption's opacity instead.
- `fligDriftUp`-style animations animate each word separately, including faked letter spacing. Some animations have
  no fade-out. Preview before using one on a title.
- **Text trims are unreliable in both directions.** In one version a positive right trim set a caption's length to
  about its start time. In a later one a *negative* trim did the same (a 3 s label became start + 3 s long, and the
  film grew by over a minute). Set the length when you create the text (`addText` `duration`) rather than trimming.
  If you must trim, re-read the element *and* `state.duration` after every trim, and correct it.
- **The default text size (24) is unreadable on a 4K canvas.** Working labels read well at size ~64 with a dark
  `backgroundPill` and opacity ~0.85.
- `addText` occasionally lands at an earlier time than asked: check and move.
- `setTextStyle` `bold: true` had no visible effect on Helvetica Neue in the version tested.
- Text position readback can be [0, 0]: verify on an export frame.

## Rendering and checking

- `captureFrame` returns the JPEG as an image item, not text. Use `capture_frames.py`, or handle the image content.
  Frames are capped at about 1920 px. Only a real export proves the final resolution: check it with ffprobe.
- `previewVideo` renders up to about 10 s. Handy for checking sound and transitions.

## Exporting

- Export runs at about 5–7 fps for 4K and almost stops while the display sleeps. Keep the display on.
- An external drive that unmounts mid-export makes the export fail when it reaches a shot on that drive.
- `exportStatus` reports `state` (preparing, exporting, complete, …), `progress` (0–1) and `outputPath`. It keeps
  reporting the last export's result after it finishes.

## Projects and connection

- **Edits reopens the last project when it starts.** A user who "just opens Edits" may have their real film open.
  Check `title` before anything else. To start a new project, ask the user to close theirs: `newProject` from the
  editor would close it for them, and closing may save.
- **Use exact titles.** Two projects can share words ("Lisbon" and "Lisbon trip 2025"). The scripts' `guard` matches
  the whole title exactly. Before creating a project, list `projects` on the home screen and pick a name that isn't
  taken.
- **If Edits quits, its MCP tools leave the session.** After a relaunch the connection can report "connected" a while
  before the tools come back. The helper scripts talk to the server directly, so they keep working: use them, or wait
  a turn.
- The tool set follows the screen: on the home screen, `title`, `state` and most editing tools don't exist.

- **Nothing carries across projects:** the clipboard is per project, and imported LUTs aren't in the catalog. Build
  later sections inside the film's own project.
- Export settings have no getter that reliably reflects the UI. **Never re-set the user's export or canvas settings.**

## Audio

- Library songs have no readable file, so you can't measure them: balance by output level (`sampleOutputLevel`) or by
  rendering a short preview.
- Royalty-free tracks are mastered at very different levels. Match by ear or by output level, not by volume numbers.
