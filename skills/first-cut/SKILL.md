---
name: first-cut
description: Makes a fast first cut (a rough cut you can watch, like a storyboard) from the user's footage with almost no questions. Offers a short preview first for people trying it for the first time. Shows them their footage, picks the best moment of each scene, assembles the draft in a new project in their video app, then sorts out colour with them (their own LUT or the app's preset) and asks how far they want to take it. Use when the user runs /video-edit-copilot:first-cut, says "make a first cut", "rough cut", "just show me something", starts a new video, or has just finished setup.
---

# First cut

The first cut is a draft to react to, not a finished film. Its job is to get the user from "a drive full of clips" to
"something I can watch" as fast as possible, so the storytelling can start. Think storyboard: the story in the fewest
shots, in the right order.

**Don't front-load questions.** People find it far easier to say what they want once they've watched something. Ask only
what you can't build without, use sensible defaults for the rest, and say which defaults you used. Taste questions come
after the cut, in `refine`, as choices anchored on what they've just seen.

## 1. Ask only this (one message, skip anything settings.json already answers)

1. **What would you like first?**
   - **A quick preview** (recommended for a first try): one day or section cut to a minute or two (for short-form, one
     short), to see the style before trusting it with more.
   - **A full first cut** of a section, or of everything.
   - **No cut, just help while I edit:** go to `assist`.
2. **Which footage:** the folder, and how much of it. Default: one day.
3. **What kind of video it is** (`video_type` in settings.json): long-form, short-form, both, or another type. This sets
   the frame and the defaults (`references/video-types.md` in `refine`). For "both", the first cut is the long film.
4. **Privacy:** anyone who mustn't be identifiable or shouldn't appear. Default: leave out shots where a stranger's
   child is recognisable.
5. **Examples:** "Is there a video you'd like it to feel like? Two or three links or files, and a line on what you like
   in each."
   - Optional for long-form and short-form.
   - **For any other type it's needed:** with no style brief in `taste-profile.md` yet, run "Learning a new type from
     examples" (`video-types.md`) before cutting, including the "Is this what you like about them?" check.
   - Save what you learn in `taste-profile.md`, and let it set the pacing, text and length.

If setup hasn't run (no `video-edit-copilot/settings.json`, or the app's MCP tools aren't in this session), run its
app, footage and log steps first. Without the MCP connection you can still make the plan and the footage map, but not
the cut.

## 2. Show them their footage

Before cutting anything, let the user see what you see. It's the fastest way for both of you to find the story.
- If the footage isn't sorted by date and place, offer the `sort` skill first. Don't sort without their yes.
- If `sort` already made a footage map of this footage, link it. Otherwise build one:
  `python3 -I <sort skill folder>/scripts/footage_map.py <footage folder> <out.html>`. Publish it if this session can
  publish a page (for example a Claude artifact), otherwise open the file.

## 3. Find the story (read-only)

Use the analysis steps in the `refine` skill, but lighter:
- **Frames:** about one frame every 2 s at low resolution. Apply the camera maker's conversion LUT if one is known;
  flat log frames are fine for choosing shots. Note each clip's subject, quality and best range.
- **Scenes:** group clips into scenes (one place or moment) using folder names, filename timestamps (a gap of 20+ minutes
  usually means a new place) and what's in the frames.
- **Speech:** transcribe only the clips you plan to use, whole clips, not snippets. Leave out stretches of conversation
  rather than muting them.
- **Background music** from shops and venues: note it. It's a copyright risk on YouTube, and music in `refine` can
  cover it.

## 4. Cut it short (defaults)

The taste profile (including any style brief from their examples) overrides all of these.
- **Short-form:** use the short-form defaults in `video-types.md`: one promise, a hook on frame 1, 1.5–3 s cuts with
  one hero hold, the safe zone, and a per-shot reframe.
- **Another type:** use its style brief.
- **Long-form:** use these:
- **Shooting order.** Inside each scene: arrive → the place → the thing you came for → a detail → leave, as far as the
  footage allows. A sign or a front shot taken on the way out can open the scene. Say so in the decision log.
- **One or two shots per moment.** Arrivals, walks and transit about 2–3 s. Most shots 3–4 s. The thing you came for
  (food, a view, the activity) 4–6 s. A day of footage usually comes out at a few minutes, and a preview at one or two.
- **Leave out** shaky, blurred or blocked shots, repeat takes, and anything with conversation.
- **Hard cuts,** a fade at the very end.
- **Sound:** each clip's own sound, evened out across cuts with **base 1.0** (there's no music yet, so the clips carry
  it: `references/music-and-sound.md` in `refine`). Cuts land on the quietest moment nearby, never in a word, and
  every clip gets a 2-frame audio fade. **No music yet:** it's placed once the picture settles, and choosing it is a
  refinement.
- **Labels:** the folder's place name on the first shot of each scene, so the storyboard reads.
  - On screen it's just the name. The decision log marks every label as a working title: names, spellings and
    addresses get checked in `refine`.
  - The recipe that passes `caption_check`: it starts on the cut and runs 3 s, centred low, size ~64 on a 4K canvas,
    with a dark pill at ~85% opacity and a quick fade that holds.
- **Privacy:** leave out shots that break their privacy answer. Blurring is a refinement.

## 5. Build it in a new project

1. **Never build over an existing project, and never close the user's.**
   - If their own project is open (Edits reopens the last one when it starts), ask them to close it first.
   - Name the new project "<video name> · first cut", for example "Lisbon day 2 · first cut".
   - List the app's projects first, and if that name is taken, add " 2".
   - Create the project, set its title, then check the title **exactly** before every write.
2. **Project settings:** the frame from the video type (`setCanvas`: 16:9, or 9:16 for short-form) before importing
   anything. For log footage in Edits, set the project to SDR.
3. **Write the plan and build it.** Plan format: `{"scenes": [{"label": "...", "shots": [{"file", "in", "out"}]}]}`.
   First move its cuts onto quiet moments (it reads the source files only), then build. For Edits:
   ```
   python3 -I <edits-playbook folder>/scripts/waveform_cuts.py plan.json [--transcripts <transcripts folder>]
   python3 -I <edits-playbook folder>/scripts/build_cut.py "<exact title>" plan.json --labels --level first --fade-out 3
   ```
   - It copies each clip into the working media folder (never touching the originals), then appends, trims and checks
     every shot.
   - It sets each clip's volume from loudness, adds the labels and the end fade, then re-reads the order and the length
     from the app.
   - It stops at the first mismatch. For another app, follow its playbook.
   - **Short-form:** the first scene's label is the hook. Use `--label-y 0.35 --label-size 80` to keep text in the safe
     band. Then reframe each shot to 9:16 as `video-types.md` describes: subject crop, stack or pan, never a blind
     centre crop. Edits' `autoReframe` and `trackObject` haven't been tested in this plugin, so try them on one shot
     first and check export frames.
4. **Colour, now that the clips are in.** Ask one question: "Do you have your own LUT for this camera?" Mention that the
   app may also have a preset for their log profile (Edits has built-in conversions). Then:
   - **They have the camera maker's official LUT:** recommend it over the app's preset. Presets aren't always the
     maker's LUT and can clip highlights.
     - Hash their LUT files first: makers sometimes ship one file under several camera names.
     - In Edits, add an adjustment layer over the whole cut (`kind: "adjust"`). If the LUT is already in Edits' LUT
       tab from an earlier project, it's one tap. Otherwise it's a one-time import that needs the screen (the user,
       or computer use if they allow it). Don't import a file Edits already lists: that makes copies.
   - **They have nothing:** apply the app's preset for their profile (`applyLUT`) and tell them where to try others.
   - **Not sure which:** compare 3–5 frames side by side (`edits-playbook/references/colour-recipe.md`).
   - Never put the conversion on phone footage or photos. Save the choice in `settings.json` (`log_lut` or
     `app_lut_preset`).
5. **Check it:**
   - one export frame per shot as a contact sheet: colour, order, labels. Look hard at the brightest shots: clipped
     whites mean the wrong conversion
   - `caption_check.py`
   - the total length
   - **the sound check** (`references/music-and-sound.md` in `refine`). A first cut is short, so render all of it
     (`render_audio.py`, about real time) and run `sound_scan.py` on it with the snapshot. With no music yet, the usual
     finds are a shot that's almost silent and a hard jump in level on a cut. Fix the accidental ones and note the
     rest in the decision log's "Sound check" line.
6. **Snapshot** the project into `video-edit-copilot/snapshots/first-cut.json`. It's the baseline `learn` compares
   against when the user edits it.
7. **Decision log:** save a short `video-edit-copilot/decision-logs/first-cut.md` covering:
   - scenes and shots
   - what was left out and why
   - the defaults used
   - the colour choice
   - working titles and anything you couldn't identify

## 6. Hand over, then ask how far to take it

Tell them briefly: the length, the number of scenes and shots, the defaults you used, and what you couldn't identify.
Ask them to watch it in the app. Then ask **one** question: where would they like to take it? Offer choices, and make it
clear that stopping is a fine answer:

- **(After a preview) The rest, the same way:** the other days or sections.
- **Story:** reorder, cut or add scenes, an opening, chapters.
- **Pacing:** what deserves more time, what should be quicker.
- **Captions:** checked place names and addresses, dish names, short notes in their own words.
- **Music and sound.**
- **More:** phone footage, voiceover, blurring someone, a title card.
- **Your own pass:** they edit it in the app themselves, and you learn from what they change (`learn`).
- **Stop here:** it's their storyboard. They finish it however they like.

Whatever they pick goes to `refine`. Also tell them they can ask for any single task in the app at any time, especially
ones they don't know how to do yet (`assist`).

## Done when

- A new project with a unique name holds the cut. Its order and length match the plan (as re-read from the app).
- Colour is chosen (their LUT or the app's preset). The contact sheet was checked, and any clipped whites were flagged.
- `caption_check` reports no problems, and `snapshots/first-cut.json` and `decision-logs/first-cut.md` exist.
- The user's own projects and source files are untouched, and the hand-over ended with the "where to next" question.
