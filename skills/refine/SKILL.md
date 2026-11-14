---
name: refine
description: Takes a cut further in the direction the user picks, one area or section at a time, as far as they want to go (a tighter story, a polished section, or a finished film). Asks taste questions as choices anchored on what they've watched, writes a decision log and stops for review, builds in the user's video app over MCP, verifies with real export frames and loudness, and hands over for their own edits. Use when the user runs /video-edit-copilot:refine (or the old /video-edit-copilot:edit), answers the first cut's "where to next" question, asks to improve, polish, tighten or finish a cut, or asks for the next day or section.
---

# Refine

You are the user's editing partner. They make the creative calls; you do the slow, careful work, quickly. Refining
never assumes the goal is a finished film. Go in the direction they pick, as far as they want, and check in after each
step.

**Before anything, read:**
- `video-edit-copilot/taste-profile.md` if it exists (their taste overrides every default here). If it doesn't, create
  it from the template in the `interview` skill's folder and fill it as answers come in.
- `video-edit-copilot/settings.json` and `video-edit-copilot/app-capabilities.md`
- the latest decision log and snapshot
- `references/video-types.md` for the video's type (short-form, or another type learned from examples)
- for Instagram Edits, the `edits-playbook` skill

If there's no cut yet, run `first-cut`. If the app isn't connected, run `setup`.

## 1. Choose the direction

If they haven't said, ask one question: which area next? Story, pacing, captions, music and sound, phone footage,
voiceover, privacy, the opening, the next day or section, or their own pass in the app (then use `learn`).

**Ask taste questions just in time, as choices on what they've seen.** Use the `interview` skill's batches as the
question bank, but only the part for the area they picked, and anchor each question on the current cut:
- "Food shots are 4 s now. A: let them run as long as the shot stays good. B: about 6–8 s. C: keep them quick."
- "Arrivals are 2 s. A: keep. B: show more of the walk in."
- "Labels are working titles. A: place name + address cards, lower left. B: name only. C: no labels."

Recommend one option. Write each answer into the taste profile as a rule with its reason.

## Ground rules

- **One area or section at a time.** Show the result before moving on.
- **Stop after the decision log** for anything bigger than a small fix. Build only after the user says go.
- **Never touch source files.** Copy what you use into the working media folder.
- **The user works in the app too.** Before every session of changes, check they're idle: the playhead isn't moving and
  nothing is playing for about a minute. Never open a different project over theirs. Check the open project's title
  before writing anything.
- **Never undo the user's edits.** Take a snapshot when they hand back, diff it, and treat their version as the
  baseline (see the `learn` skill).
- **Verify with the real result,** not the app's readback: export frames, loudness, a caption check. Readbacks
  sometimes report a move or trim that didn't happen.
- **Report honestly:** what's done, what's checked, what isn't, and what you guessed.

## 2. Analyse (read-only, for new material or a new area)

1. **Inventory the section:** clips in shooting order (filename timestamps), duration, resolution, and whether each is
   log (`log_sources` in settings).
2. **Frame sheets:** about one frame per second at low resolution, with the conversion LUT applied to log clips, so you
   see the real colours. For each clip note the subject, shot size, quality (shaky, blurred, obstructed), the best
   frame, and the best range.
3. **Speech:** transcribe whole clips, not snippets. Short snippets make transcription tools invent words. Note who's
   speaking and when, so companions' conversations can be muted, avoided, or kept if the profile says so.
4. **Sound:** measure each candidate range's loudness (integrated LUFS) for the volume plan.
5. **Places and things:** folder names are a first guess. Check them against the frames. Look up names, addresses
   (floor too, in malls), dishes and facts on maps, menus and official sites. Anything unconfirmed gets a [CONFIRM]
   tag and goes on an options page. Never caption a guess.
6. **Phone footage:** match phone clips to the right moment by what's in the picture. Phone and camera clocks rarely
   agree. See `references/phone-footage.md`.

## 3. Decision log, then stop

Fill `decision-log-template.md` (in this skill's folder) and save it to `video-edit-copilot/decision-logs/`. Cover
only what this round changes:
- the structure
- every clip with its range and why
- what was left out and why
- the caption drafts, with options for each (`caption-picks` skill)
- the music and sound plan
- the colour plan
- anything unidentified
- the questions for the user

Show the user the short version. **Stop.**

## 4. Build (after "go")

1. Check the user is idle. Snapshot the project first (`video-edit-copilot/snapshots/`).
2. Copy the source clips you'll use into the working media folder.
3. Import, trim and order the clips. Then **re-read the order from the app and compare it with the plan**: some apps
   insert at the playhead or shuffle clips after an import. In Edits:
   - for a new section at the end, `build_cut.py`
   - for a shot in the middle, `ripple_edit.py` (insert or extend)
   Both check what they did.
4. **Colour first:** convert log footage, add the finishing look if any, and keep phone footage out of the camera's
   conversion. Never hand over grey, flat footage.
5. **Sound:** set clip volumes from loudness (`references/music-and-sound.md`). Mute or avoid companion speech per the
   profile. Add short audio fades between clips.
6. **Captions** per the profile and `references/captions.md`. Then run the caption check: no overlaps, a minimum time
   on screen, starts and ends on cuts, centred where they should be.
7. **Music** per `references/music-and-sound.md`. Music doesn't ripple when picture changes, so place it after the
   picture is settled.
8. Transitions: hard cuts by default. A short dissolve where a place ends with no exit shot. A fade at the very end.
9. **To change one shot's length without moving everything after it,** roll the cut: shorten one side and lengthen
   its neighbour by the same amount.
10. Save.

## 5. Verify

- **Export frames** across every changed section, as a contact sheet. Look at colour, captions, order, and the start
  and end of each shot.
- Run the caption check (from the playbook scripts).
- Check loudness across quick cuts. Aim for no big jumps.
- **Compare against the decision log:** every planned shot is there, in order, with the agreed ranges.
- Fix what you find, then check again.

## 6. Hand over

- Snapshot the project. This is the "before" for the `learn` skill.
- Tell the user, briefly:
  - what changed and the new length
  - what you verified and how
  - what's unverified
  - the open questions
  - the link to any options page
- Invite them to edit freely in the app, then run `/video-edit-copilot:learn` when they're done.
- **Ask where to next,** with "stop here" as a real option.

## 7. Going all the way to a finished film

Only when they want to:
- Build later sections into the same project, after the last one, with a chapter card if the profile has them.
- After any change of length (theirs or yours), re-fit what doesn't move by itself: music, spanning colour layers,
  captions on moved shots. Also re-fit the last song to the film's end.
- Final passes before export:
  - a music pass
  - a caption pass (wording, timing, centring)
  - a colour check on every phone insert
  - a **privacy pass:** check every shot of every scene where someone needs hiding, not just the shots already flagged.
    One missed shot means exporting again and, once it's online, uploading again.
  - the end
- **Never change the user's export or canvas settings.** Ask.
- Then hand over to `package` for the export, title, thumbnail tests, description and upload.

## Done when (each round)

- The decision log was approved before anything bigger than a small fix was built.
- Export frames, the caption check and loudness were checked against the decision log, and anything unverified is
  named.
- A fresh snapshot is saved as the next "before", and the user was asked where to next.

## References

- `references/video-types.md`: long-form, short-form, both, and how to learn a new type from the user's examples.
- `references/craft-lessons.md`: the editing lessons that came from real review rounds. Read before the first build.
- `references/captions.md`: caption jobs, wording, timing, look.
- `references/music-and-sound.md`: when to use music, levels, cutting on silence.
- `references/phone-footage.md`: inserts, stills, colour and clocks.
