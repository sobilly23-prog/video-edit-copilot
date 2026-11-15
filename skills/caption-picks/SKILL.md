---
name: caption-picks
description: Builds an options ("picks") page for captions and other close calls in a Video Edit Copilot edit. Each question shows a clean frame of the shot with each option previewed on it, and the user answers like "1B, 2A, 5C". Use when captions, place names, dish names, hold lengths or inserts need the user's choice, or when the user asks for options.
---

# Caption picks

People find picking far easier than describing. So every caption (and any close call: which take, how long to hold,
whether to add a phone insert) goes on a page of options. Option A is what's already in the film, or what you
recommend. The user answers with letters, or types their own.

## Build the page

1. **Get a clean frame for each question,** with no captions burned in. The page draws each option on the frame
   itself, so a frame that already carries the caption shows it twice. For Edits, use the playbook's `tl_frames.py`:
   it pulls graded frames straight from the source files. Use 640 px wide frames.
2. **Write the questions file** (JSON):

```json
{
  "title": "Day 2 Caption Picks",
  "h1": "Day 2: captions to pick",
  "intro": "Option A is in the film now. Pick another or type your own, then copy your picks back.",
  "key": "day2picks",
  "label": "Day 2 picks",
  "questions": [
    {
      "kind": "line",
      "where": "Day 2 · 3:41",
      "tc": "3:41",
      "img": "frames/q01.jpg",
      "alt": "Street outside the café",
      "title": "Bridge from the café to the market",
      "note": "Why this needs a line, and any facts or sources.",
      "options": [
        { "text": "Across the road to the night market", "why": "In the film now" },
        { "text": "Next, the night market" },
        { "text": "(no line here)" }
      ],
      "links": [ { "label": "Market on the map", "url": "https://…" } ]
    }
  ]
}
```

   - `kind` is `line` for a centred caption, or `card` for a place card, written as `"Name | Address"` so both lines
     preview.
   - Give 2–4 options. Make them real alternatives (different length, angle or level of detail), not rewordings of
     each other.
   - Add a `note` when facts were looked up, and a `links` entry for sources (menus, map listings) so the user can check.
   - Include the optional lines you decided against, with "(no line, as now)" as option A.
   - **Every question starts on option A, and "Copy my picks" sends A for any question the user didn't touch.** So for
     opt-in ideas ("add a closing shot here?"), make A the "no change" option. Otherwise an untouched idea reads as a
     yes.
   - **Sound questions get sound clips.** A silence you weren't sure was meant, a level jump, a song change: a frame
     can't show it. Add `"audio": [{"label": "Now", "file": "q03-now.mp3"}, {"label": "With the fix",
     "file": "q03-fix.mp3"}]` to the question, each clip about 6 s around the moment. Cut them from a render
     (`render_audio.py` in the playbook), then `ffmpeg -i in.wav -ss <s> -t 6 -b:a 96k q03-now.mp3`.
   - **Everything the user needs to review goes on the page,** not in the chat message: each item with its timecode,
     a frame and, for sound, the clips. The message links the page.
3. Build it with `scripts/make_picks.py questions.json out.html` (in this skill's folder; it uses
   `scripts/picks_template.html`). Images and sound clips are embedded, so the page is one file.
4. **Share it.** If this session can publish a page (for example a Claude artifact), publish it and give the link.
   Otherwise open the HTML file locally.

## Read the answers

The page's "Copy my picks" button gives something like:
`Day 2 picks: 1B, 2A, 3: "something about the sauce", 4C`
- A letter picks that option.
- Quoted text is the user's own wording, or a note asking you to write it ("not lunch, more like a snack"). Write the
  final line and show it.
- Notes in the user's message beat the picks.
- "No line here" means delete it.

Apply with the `learn` skill's steps: apply, check overlaps and timing, then report the final wording.
