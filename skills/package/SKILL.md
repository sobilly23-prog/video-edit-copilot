---
name: package
description: Gets a finished cut out of the app and ready to publish. Covers the last checks before export, watching the export (keeping the computer awake), checking the exported file, then the upload kit for YouTube - title options, thumbnails built from the film's own frames, a thumbnail and title A/B test plan, a description with chapters and map links, tags, a pinned comment, end screen, cards and upload settings - on one page the user can copy from. Use when the user runs /video-edit-copilot:package, says the film is done, asks to export, or asks for a title, thumbnail, description, tags or an A/B test.
---

# Package

A film people never click on doesn't get watched. This skill turns the finished cut into an upload: a checked export,
packaging built from the film itself, and a test plan, so the user learns what works for *their* audience instead of
guessing.

**Short-form** (Reels, Shorts, TikTok) packages differently:
- a title or first line with a hook, plus 2–4 hashtags
- a cover frame
- the safe zone checked in the platform's preview
- on YouTube, the "related video" link to the long film

See "Short-form" in `references/video-types.md` in `refine`. The thumbnail A/B tests below are for long-form.

Read the taste profile's **Packaging** section first. If they have a channel, match its existing series format
(title shape, thumbnail style, description layout), so the videos read as a series.

## 1. Last checks before export

Exporting is slow, and a mistake found after upload means exporting and uploading again (YouTube can't replace the
video file of an upload; see step 9). So check first:
- **Privacy:** every shot of every scene where someone must be hidden, every 2 s or so, not just the shots already
  fixed. One missed shot is the most common reason to export twice.
- **Captions:** spelling, names, and that each sits on its own shot.
- **Music licences:** for YouTube, royalty-free only. In-app "licensed" music may only be cleared for that app's
  platform.
- **The end** (fade, end card), and the film's length.

## 2. Export

- **Never change the user's export or canvas settings.** They start the export, or confirm the settings first.
- **Keep the computer awake with the display on** for the whole export. Some apps render far slower, or almost stop,
  when the display sleeps (Edits did). On macOS, `caffeinate -d -i` or "Turn display off: Never" in settings.
- **Keep every drive the project reads from connected.** An export fails when it reaches a shot on a drive that's gone.
- **Set expectations:** a long 4K export can take one to two hours. Measure the real rate after ten minutes rather than
  trusting the app's estimate.
- **Watch it** in the background and report when it ends or stalls. For Edits: the playbook's `export_watch.py`
  (`--path` for each external drive). It keeps a Mac awake while it runs.

## 3. Check the exported file

- `ffprobe`: duration matches the project, resolution, frame rate, audio present.
- Frames from the **exported file** (not the app) at each privacy fix and each caption changed since the last export.
- Then tell the user it's ready, with the file path.

## 4. Title options

Write 3–4 options on a picks page (`caption-picks`, or the kit page in step 8):
- Match their series format if they have one.
- About 50 characters show in a phone feed. Put the place and the promise first.
- Keep it general enough to be true of the whole film. Don't list one-off moments.
- No clickbait the film doesn't pay off.

## 5. Thumbnails from the film's own frames

1. **Pick candidate frames** from graded footage at full resolution (for Edits, the playbook's `tl_frames.py` with
   `--w 3840`). Good thumbnails usually show one clear subject: a face with a real expression, the hero dish, or the
   place at its best. Avoid busy frames.
2. **Build 3–5 variants** with `scripts/make_thumbnails.py <spec.json> <out_dir>` (in this skill's folder). It writes
   HTML, renders each with headless Chrome at 2x, scales to 1280×720 JPG, and makes `preview_feed.jpg` at phone-feed
   size. Layouts worth trying:
   - **A single beautiful shot** with a person in it, title over the sky or a plain area.
   - **Three tall panels** (place, food, the thing you did): common for travel videos, and it previews the variety.
   - **A single shot without a person,** to test whether a face matters for this audience.
3. **Use the film's own title look** (font and colour from its title card) so the thumbnail matches the film.
4. **Check at feed size:** the title must still read at 168 px wide, and it mustn't cover the subject. Mirroring a shot
   flips any signs or text in it, so prefer re-framing.
5. Show them as picks. They choose the main one.

## 6. Plan the A/B test

YouTube Studio can test up to 3 thumbnails (and titles, where available) on one video: **Test & Compare**, on desktop,
with advanced features on. It shows each version to a share of viewers for up to about two weeks and keeps the one with
the most **watch time**, not clicks. Check the current rules in YouTube's help; they change.

Design the test so the result teaches something:
- **Change one thing between versions,** and keep the title text the same on every thumbnail so only the picture
  changes. For example: 1 = single shot with a face, 2 = three panels with a face, 3 = single shot without a face.
  Then the result answers "does a face help?" and "does one shot beat three panels?".
- **Version 1 is their favourite.** It's what stays if the test has no clear winner, which is common on small
  channels.
- **Write down the result** when the test ends (which won and by how much) in the taste profile's Packaging section,
  so the next video starts from what worked. Ask the user to tell you, or to paste the result.

## 7. Description, tags, comment, end screen

- **Description:**
  - A one- or two-line intro that says what and where.
  - **Chapters:** the first at 0:00, at least three, each at least 10 s long. Take them from the film's sections.
  - **A guide to every place** in the order it appears, each with a one-line note and a map link. A search link works
    everywhere: `https://www.google.com/maps/search/?api=1&query=<name>%2C+<address>`. Open a few to check they land
    on the right place. Places inside a mall or food hall often have no listing of their own: link the hall.
  - Music credits, if a licence asks for them.
  - YouTube's limit is 5,000 characters, with no `<` or `>`.
- **Tags:** plain search phrases people would type, under 500 characters in total.
- **Pinned comment (optional):** a question viewers can answer from their own experience. If it includes the user's own
  answer, offer it as a draft for them to rewrite.
- **End screen:** one or two elements (the next or previous video in the series, subscribe) in the last 5–20 s. Leave
  space for them when designing the end card, and keep them off any text.
- **Cards:** only where the film mentions another video.
- **Upload settings:**
  - category and video language, location, recording date
  - not made for kids
  - paid promotion
  - **altered or synthetic content:** blurring doesn't count, but a cloned or AI voice narrating as a real person usually
    does
  - a playlist for the series

## 8. One page for all of it

Put everything in upload order on one page:
1. the chosen thumbnail and the test set
2. title options
3. the description, tags and pinned comment, each with a copy button
4. end screen, cards and settings

Publish it if this session can (for example a Claude artifact), otherwise save the HTML in the project. Save the
plain-text files too (`description.txt`, `tags.txt`), and the thumbnails in a `final/` folder named in upload order:
`1_MAIN_…jpg`, `2_test_…jpg`, `3_test_…jpg`.

## 9. Uploading again

YouTube can't swap the video file on an existing upload: a new file is a new video with a new link.
- **Upload as Private first,** watch it on YouTube, and publish only when it's right.
- If they must re-upload: put the old one on Private straight away if it shows something it shouldn't. Upload the new
  file and use **Reuse details** (on the Details step) to copy the title and description. Then add the thumbnail again,
  and the end screen (its editor can import from another video). Delete the old video only if it has no views or
  comments worth keeping. Otherwise leave it private.
- YouTube Studio's own editor can blur or trim an uploaded video without re-uploading, but it can't change on-screen
  text.

## Done when

- The exported file was checked with ffprobe and with frames from the file itself.
- The kit page (or the files) holds the title options, thumbnails, test plan, description, tags and settings.
- Nothing was uploaded or published for the user. They upload it themselves.
