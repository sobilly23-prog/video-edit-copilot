# Changelog

## 0.4.0 (2026-11)

Sound editing, from real viewer feedback. Viewers of a finished film said the sound went silent in places and that
some sounds "cut in". A scan of the exported file showed every one of those came from the edit, not the render: title
cards with no sound, shots muted over a sparse song, and big level jumps on cuts. Sound is now checked, not assumed.

**Required at every hand-over** (after the build, every review round, every pass of the user's own, and before export)
- **Frame audio transitions:** a 2-frame audio fade at every cut where the sound jumps. A continuous split (one take cut
  in two) gets none, since a fade there only makes a dip.
- **Waveform cuts:** cuts land on the quietest moment within about ±0.25 s, between words and hits. Planned cuts are
  moved before building. On a built film the copilot slips its own shots and puts the user's own cuts on the review
  page instead of changing them.
- **The sound check:** render the changed stretch (or take the export), scan it, and give every finding a verdict.
  Intentional silence stays; accidental gaps, cut-ins and jumps get fixed; anything unsure is flagged for the user,
  with "now" and "with the fix" sound clips on the review page. The decision log gets a "Sound check" line.

**New rules** (`refine/references/music-and-sound.md`)
- Silence is fine when it's meant.
- Title and chapter cards need a sound bed. Trim a song's silent intro, or start the next song about 1 s early.
- Mute to 0 only under a steady bed. Never let a sparse song intro be the only sound.
- Every silent picture (a photo, a still, a title graphic) gets a bed baked into a copy of the clip.
- No more than about 6 dB across any cut.
- A place's own sound leads where it's the point. Draft fewer songs. The user's own music arrangement is the one
  carried forward.

**New scripts** (Edits playbook)
- `sound_scan.py` (read-only): dropouts, near-silence, cut-ins and cut-outs, and level jumps on cuts, each placed on a
  cut or mid-shot. It works on any audio or video file.
- `waveform_cuts.py`: moves a plan's cuts onto quiet moments and out of speech before building. It reads source files
  only.
- `audio_fades.py`: adds the 2-frame fades. `--check` audits them without changing anything.
- `waveform_slip.py`: slips built shots onto quiet moments without moving anything else. `--dry` first.
- `render_audio.py`: renders a stretch's real mix (volumes, fades, library songs) through Edits' preview renderer.
- `caption-picks`: picks pages can carry sound clips, so sound questions get "now" and "with the fix" clips.

**Tested**
- `sound_scan.py` gave the same findings as the original script it came from on a 30-minute export (159 findings,
  type for type).
- Run against the test project's own files: `waveform_cuts.py` (dry run: 27 cuts moved, plan untouched) and the
  `audio_fades.py --check` audit.
- The fades and slip logic were tested against a mocked app: continuous splits get no fade, and the user's own cuts
  are listed, not changed.
- `render_audio.py` and the picks page's audio player were ported unchanged in behaviour from the author's own tested
  versions.
- **Not yet tested live in the plugin:** the write paths of `audio_fades.py` and `waveform_slip.py`, and
  `render_audio.py`.

## 0.3.0 (2026-11)

From the first full test drive of 0.2.0 (setup → sort → first cut in Instagram Edits) and the reviewer's notes.

**Flow**
- **Onboarding asks what kind of video you're making:** long-form, short-form, both, or something else.
  - Short-form gets its own defaults: hook on frame 1, 1.5–3 s cuts with one hero hold, the safe zone, per-shot
    reframing (never a blind centre crop), and short-form packaging.
  - Any other type is learned from 2–3 of the user's example videos. The copilot measures them, writes a style brief,
    asks "Is this what you like about them?", and asks for more examples if it's still unclear.
- **Setup asks which editing app you use.** It says plainly that the plugin was built and tested on Edits, and lists
  which other editors have an MCP server (DaVinci Resolve 21.1+ Studio officially; Premiere Pro, Final Cut Pro and
  CapCut through community servers).
- **Setup checks which project is open.** Edits reopens the last one at launch, so the copilot asks you to close yours
  before it creates a new project.
- **Colour left setup.** It now happens after the clips are in the app. The first cut asks whether you have your own
  LUT for your camera, recommends the camera maker's LUT over the app's preset, and falls back to the preset. LUTs are
  chosen by log profile.
- **The first cut offers a quick preview first** (one day, a minute or two), plus one optional "what should it feel
  like" line.
- **Sort is chronological by default:**
  - place (from your itinerary), then day, then category and place
  - suggested categories you can rename or add to
  - review folders for travel days and stray dates

**New scripts**
- `setup/scripts/analyse_reference.py`: read-only study of an example video. It reports length, aspect, shots, cuts
  per minute, shot lengths, the hook, loudness and near-silence, and makes a shot sheet and a hook sheet. In testing
  it found all 28 cuts of a known 28-shot cut, at the exact times.
- `sort/scripts/inventory.py`: read-only footage inventory (clips and minutes per folder, formats, camera model, colour
  tags, broken files).
- `edits-playbook/scripts/build_cut.py`: builds a cut from a plan. It copies, imports, trims, sets levels and adds
  labels, checks every shot, then checks the order and length. 28 shots took under a minute in testing.
- `sort_footage.py`: `--itinerary`, `--categories` / `--no-categories`, and empty category and inbox folders (undone
  with the rest).

**Fixes**
- Project title checks are exact, never a substring: "Lisbon" no longer matches "Lisbon trip 2025".
  `safe_delete.py` now takes the project title too.
- The first cut's volume uses base 1.0 (no music yet). Base 0.3 is for clips under music; the old default made a cut
  with no music about 10 dB too quiet.
- `capture_frames.py --sheet` accepts a path.
- Quirks file:
  - text trims misbehave in either direction, so set the length in `addText`
  - the default text size is unreadable at 4K
  - Edits keeps imported LUTs for every project (re-importing makes copies)
  - `getElement` reads imported LUTs back
  - `addAdjustmentLayer` needs `kind: "adjust"`
  - the MCP tools drop out when Edits restarts
- `log_sources`: warns that `_D\.MP4$` matches every recent DJI file, log or not.
- The footage map warns about page size for big folders and suggests fewer workers while the app is open.
- The first cut doesn't rebuild a footage map that sort already made.
- Every script prints its usage instead of a traceback when arguments are missing. All scripts run on the macOS
  system Python (3.9).
- `build_cut.py`: `--label-y` and `--label-size` (for the short-form safe band). Labels are added after all the shots
  (Edits won't let text run past the end of the timeline).
- `export_watch.py` checks every 15 s and judges a finished export by its file when the app resets to idle.
- Each main skill ends with a "Done when" checklist.

## 0.2.0 (2026-11)

First cut first: setup → sort → first-cut → refine, with assist and package alongside. The interview became optional.

## 0.1.0 (2026-11)

First version: setup, interview, edit, learn, caption-picks, voiceover and the Edits playbook.
