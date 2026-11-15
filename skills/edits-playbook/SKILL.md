---
name: edits-playbook
description: Instagram Edits (Mac) specifics for Video Edit Copilot - connecting its local MCP server, the helper scripts (cut builder, snapshot, diff, wait-until-idle, safe delete, export-true frames, clean graded frames, caption check, music and layer re-fit, ripple insert/extend, loudness-matched volume, and the sound check: waveform cuts, audio fades, audio render and sound scan), the colour recipe, music workflow, and the app's known quirks. Use whenever the copilot edits in Instagram Edits, or when an Edits tool call behaves unexpectedly.
---

# Instagram Edits playbook

Everything here was learned building a long film in Edits for Mac over its MCP server ("metapilot-native"). Tool names
and behaviour can change between Edits versions. Read `video-edit-copilot/app-capabilities.md` and each tool's schema
before relying on a detail, and add what you learn to `references/gotchas.md`.

## Connect

- Edits → Settings → Automation → **Enable Automation Server**. Edits shows a ready
  `claude mcp add --transport http --scope user metapilot-native <url> --header "Authorization: Bearer <token>"`
  command. The **user** runs it in a terminal, then starts a new Claude Code session.
- **Never ask for, print or store the token.** The helper scripts read the URL and header from the user's own
  `~/.claude.json`.
- The tool set follows the app's screen: home screen versus an open project. Call `getCapabilities` first. If tools
  fail with "connection refused", Edits is closed.

## Working alongside the user

The user is often in the app at the same time: reviewing, playing, scrubbing, switching projects.
- Before changing anything, run `scripts/wait_idle.py` (in the background) until the app has been untouched for a
  minute or more.
- Check the open project's title before every write, exactly (not part of it). The scripts' `guard` does this.
- Edits reopens the user's last project when it starts. If it's theirs, ask them to close it before you create one.
- **Never open a project over the user's.** Ask them to open the right one.
- Imports and the audio panel's "+" land **at the user's playhead**: check `state` right before adding anything.
- **Never change their export or canvas settings.**

## Helper scripts

Run them from the project folder: `python3 -I <this skill's folder>/scripts/<script> …`

| Script | What it's for |
|---|---|
| `build_cut.py "Title" plan.json [--labels] [--level first] [--fade-out 3]` | Builds a cut from a plan: copies, imports, trims, levels and labels every shot, checks each one, then the order and length. |
| `snapshot.py out.json "Title"` | Read-only snapshot of every element. Take one before each hand-over and after each review. |
| `diff_edits.py before.json [--after after.json]` | What the user changed: the input to the `learn` skill. |
| `wait_idle.py [secs]` | Blocks until the user has left the app alone. |
| `safe_delete.py "Title" <id>` | Deletes exactly one element or nothing (selecting by id can fail silently). |
| `capture_frames.py dir t… [--sheet s.jpg]` | True export frames (grade, captions, fades) for verification. |
| `clipmap.py snapshot.json` | Maps clips to source files (needed by the next two). |
| `tl_frames.py snapshot.json dir t0-t1/step [--sheet s.jpg]` | Clean graded frames, no captions, from the source files. For analysis and picks pages. |
| `caption_check.py` | Overlaps, too-short captions, captions that start just after a cut, alignment. Read-only. |
| `remap_layers.py "Title" old.json [--dry]` | Re-fits music and adjustment layers to their scenes after clips change length. |
| `ripple_edit.py "Title" insert/extend/els …` | Insert a trimmed clip before a given clip, or lengthen one, and report everything that moved. |
| `loudness_volume.py file in out` | LUFS of a range and the volume that evens out quick cuts. |
| `waveform_cuts.py plan.json [--transcripts dir] [--dry]` | Before building: moves the plan's cuts onto the quietest moment nearby, out of speech. Reads source files only. |
| `audio_fades.py "Title" t0 t1 [--check]` | 2-frame audio fades at every cut where the sound jumps (none on a continuous split). `--check` audits without changing anything. |
| `waveform_slip.py "Title" t0 t1 --dry [--mine build-log.json]` | On the built film: slips shots so their cuts land on quiet moments, without moving anything else. Lists the user's own cuts instead of changing them. |
| `render_audio.py out.wav start length "Title"` | Renders a stretch's real mix (volumes, fades, library songs) through the app's preview renderer. About real time. |
| `sound_scan.py file [--start s] [--snapshot snap.json]` | Read-only: dropouts, near-silence, sounds cutting in or out, level jumps on cuts, each placed on a cut or mid-shot. Run on a render or the exported file. |
| `export_watch.py [--path /Volumes/Drive]` | Watches an export the user started: progress, speed, time left, a drive that disappears. Keeps a Mac awake while it runs. |

## Building a section

For a new cut, `scripts/build_cut.py` does steps 1–3 and the working labels in one go (28 shots in under a minute in
testing). By hand:
1. Copy the used source clips into the working media folder. Edits' sandbox can't read external drives.
2. Import in order. **`importMedia` inserts at the playhead,** not at the end: seek to the right place first (end of
   timeline, or the start of the clip you're inserting before). Trim each clip to its range and set its volume.
3. **Re-read the clip order** and compare it with the plan. Edits has shuffled clips after an import.
4. Colour (`references/colour-recipe.md`), then captions, music, transitions.
5. `saveProject`. If the viewer shows the wrong shot after big reorders: save, `closeProject`, `openProject`.

## Captions in Edits

- `addText` (set the length here: `duration`), then `setTextFont`, `setTextStyle` (size, alignment, colour),
  `setTextPosition` (x, y as 0–1 of the frame), `setEmphasis` (`backgroundPill` with a colour), `setTextAnimation`.
- The default size (24) is unreadable on a 4K canvas: about 64 for a working label.
- **Animation:** the catalog's `fadeIn` spreads the fade over the caption's **whole** length, so it's only fully
  visible on its last frame. A quick fade that holds (`fligFadeBox` in the version tested) reads much better.
- **The pill's colour transparency is ignored** (it renders opaque). Set the caption's own opacity (`setOpacity`,
  about 0.8) to soften it.
- **Text position readback can show [0, 0].** Check position on an export frame instead.
- **Trimming a text element is unreliable in both directions.** Depending on the version, a positive or a negative
  right trim has set a caption's length to about its start time, and the film suddenly ran much longer. Set the length
  in `addText`. If you must trim, re-read the element and `state.duration` after every trim.
- `reorderClip` **carries the captions sitting on a clip** with it. Re-seat any caption that described a neighbour.

## Music in Edits

- Adding a song from Edits' music library by tool (`addSongToComposition`) failed to download in the version tested.
  The user adds the track in the Audio panel (the Recent tab), or computer use clicks it. Then place sections by
  tool: trim, move, fades, volume.
- **Check each track's licence.** The tool reports `isRoyaltyFree`. In-app "licensed" tracks may be cleared only for
  Instagram, so use royalty-free tracks for YouTube.
- **Music never moves when the picture changes.** Re-fit with `remap_layers.py` from a snapshot taken when it was
  right. Then re-list the music: a `move` has reported success without happening.
- **Ending:** a dissolve transition from the last clip with no "to" clip fades to black. Edits uses about **half** the
  stored duration, so a stored 5 s gives about 2.6 s. Fade the last clip's audio, and keep the music's fade at least as
  long as the picture's.

## Sound in Edits

The sound check itself is in `music-and-sound.md` (in `refine`). The Edits side of it:
- `setFade` on a video clip fades its **audio** only. The picture stays a hard cut, which is what audio fades want.
- `slipClip` changes which moment of the source a clip shows while keeping its place and length: the way to move a
  cut onto a quiet moment without rippling captions and music.
- `replaceElementMedia` swaps a clip's file and keeps its place and length. Use it to swap in a copy of a still with a
  sound bed baked in, then set its volume and fades.
- Library songs have no file you can read. To hear or measure them in the mix, render the stretch
  (`render_audio.py`, which joins `previewVideo` renders of up to 10 s each).
- `quietPoint` and `audioLevels` analyse a source file's sound too. The scripts read the files with ffmpeg instead, so
  they work the same in any app.

## Exporting

- **The user starts the export,** with their own settings. Never call `setExportSettings` on their project without
  asking. Only a real export file proves the final resolution (frame captures are capped at about 1920 px).
- **Speed (Edits for Mac, tested):** about 5–7 frames a second for 4K HEVC at 24 fps, so a 30-minute film takes roughly
  1½–2 hours. Edits renders frame by frame on about one CPU core, so a faster Mac barely helps.
- **The display must stay on.** With the display asleep the export almost stopped: one 2-hour export took 4. Run
  `export_watch.py` (it holds `caffeinate -d -i` while it runs) or have the user set "Turn display off: Never".
- **Every drive the project reads must stay connected.** An export failed at 57% when an external drive unmounted:
  it stops when it reaches a shot on that drive. Pass each drive with `--path` so you hear about it at once.
  `mediaStatus` lists every media item with its file path and whether the file exists; check it before an export.
- **Before exporting,** run the privacy rescan and caption check (see the `package` skill). Then check the exported
  file with ffprobe and frames from the file itself.
- **Don't delete the working media folder after exporting** unless the user is sure the film is final. The project
  needs those files to edit or export again, and generated files there (blurred or stabilised copies, title cards)
  can't simply be copied back from the camera originals.

## What the MCP can do that Edits' screens can't

Worth knowing, and worth using:
- **Exact values with no control in the UI,** such as a LUT's strength (`updateCatalogItem` intensity).
- **Bulk changes:** restyle or retime every caption in one pass.
- **Read the whole project:** every element with exact timings (`elements`, `getElement`). This is what makes
  snapshots, diffs and learning from the user's edits possible.
- **Export-true checks:** `captureFrame` (one frame) and `previewVideo` (up to about 10 s) render through the export
  pipeline.
- **Audio analysis:** loudness and output level (`sampleOutputLevel`), the quietest point near a cut (`quietPoint`),
  pauses, onsets and beats.
- **AI analysis:** transcription (`transcribeClip`), shot and cut detection, people and face detection
  (`detectSubjects`), and following an object described in words (`trackObject`).
- **Full catalogs** of effects, transitions, filters, LUTs and text animations (`listCatalog`, `listEffects`), including
  some effects that don't appear in the desktop panels.
- **Voiceover:** teleprompter, recording and text-to-speech tools (see the `voiceover` skill).

## References

- `references/colour-recipe.md`: log conversion and finishing look with adjustment layers, including the steps that
  need the screen.
- `references/gotchas.md`: every quirk found so far, and what to do about it.
