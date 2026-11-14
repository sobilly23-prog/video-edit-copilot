# Video types

Setup asks what kind of video the user is making. The answer picks the defaults the first cut and every refine round
start from. The taste profile overrides them as it grows.

**Be honest about coverage.** Long-form personal and travel video is what this plugin was built and tested on.
Short-form has sensible defaults but less testing. Anything else is learned from the user's own examples, and the first
cut of a new type won't be perfect: say so up front.

| Type | Coverage | Starts from |
|---|---|---|
| **Long-form** (YouTube-style, several minutes and up, 16:9): travel vlog, day in the life, a trip or event film | Built and tested | `first-cut` defaults, `craft-lessons.md`, `captions.md`, `music-and-sound.md` |
| **Short-form** (Reels, Shorts, TikTok: vertical, under a minute) | Defaults below, lightly tested | **Short-form** below |
| **Both** (a long film, plus shorts cut from the same footage) | As above | The long film first. Shorts come after it's locked, each linking to it |
| **Anything else** (wedding, event recap, product, tutorial, talking head, real estate, sport…) | Not built in | **Learning a new type from examples** below |

## Long-form

Use the defaults in `first-cut` and the craft references:
- shooting order
- arrivals quick, and what you came for given time
- a label per place
- each place's own sound evened out
- music added once the picture settles
- 16:9

## Short-form

Platform rules change often. Check the current ones before relying on a number. As of late 2026:
- **Length:** 15–35 s suits most personal shorts, and under 60 s is the safe ceiling. YouTube Shorts and Instagram Reels
  allow up to 3 minutes, but outside music can get a long short claimed or blocked. Royalty-free music only.
- **Frame:** 9:16, 1080×1920. A 9:16 window cut from 4K landscape (1215×2160) still exceeds 1080×1920, so crops stay
  sharp, with room for a gentle push-in.
- **One clear promise.** "One place", "a list of N", "a day as an itinerary", "a process" (cooking, pouring, making), or
  "a teaser" for a long film. Pick one per short.
- **Hook on frame 1:**
  - one line under 10 words, in the upper middle (about 30–40% down)
  - the first frame and the first second decide whether people swipe away
- **Pacing:**
  - cuts every 1.5–3 s, with one hero hold of 4–6 s on the payoff
  - the payoff by about 70% of the length
  - end on **one** ask *or* a loop back to the first frame, never both
- **Safe zone:**
  - the platform's buttons sit on the right, and the caption and handle at the bottom
  - keep text and faces in the centre band: roughly clear of the right 15%, the bottom 25% and the top 10%
  - check in the platform's own preview
- **Text:** the hook, then a short name per stop at most. Same upper-middle band. Bigger than long-form labels.
- **Sound:** a process short can run on its own sound turned up. Otherwise light music under the clips' sound.
- **Reframing landscape footage. Never a blind centre crop.** Choose per shot:
  - detail (food, hands, a pour): a centre crop, nudged to the subject
  - an off-centre subject: the crop moved to it, held or slowly following
  - a wide establishing shot: a **stack** (the wide on top, its detail below), or the wide over a blurred copy of
    itself
  - a long calm wide: a slow pan across the frame
  - native vertical clips: full frame

  Show the crop choices on a picks page (`caption-picks`) when they matter.
- **In Instagram Edits:**
  - `setCanvas` to 9:16
  - `autoReframe` keeps a face, a person or the centre in frame, and can make a two-panel stack
  - `trackObject` follows anything you describe ("the bowl"), and its boxes can drive `setTransformKeyframes`
  - `splitScreen` builds a stack
  - These haven't been tested in this plugin yet. Try them on a throwaway project first.
- **Build from the source clips, not from a long film's export:** the export has its captions burned in.
- **Packaging:**
  - a title with 2–4 hashtags
  - a first line that's a second hook or the question
  - a cover frame
  - on YouTube, the "related video" link to the long film
  - Measure "viewed vs swiped away" first, then the average % viewed. Loops can take it past 100%.

## Both

- Make the long film first.
- While building it, flag short candidates in each decision log: a strong single moment, a process, a list across
  places.
- Cut the shorts after the long film is locked, 3–5 per long film is a good start. Post a teaser when the film goes up.

## Learning a new type from examples

For a type that isn't built in, or whenever the user says "make it like this", learn the style from examples instead
of guessing. Use the examples only to understand the style. Never copy their footage, words, music, graphics or
on-screen identity.

1. **Ask for 2–3 examples** close to what they want, and one line on what they like in each.
   - Files they can share are best.
   - Links work too. Read what's public (title, description, chapters, transcript), and ask them to point at moments
     ("the cut at 0:12").
   - Don't download videos from platforms whose terms forbid it. Ask the user for a file instead.
2. **Study each one.** For a file, run:
   ```
   python3 -I <setup skill folder>/scripts/analyse_reference.py <video> --out video-edit-copilot/references/<name>
   ```
   It reports:
   - length, frame and aspect
   - the shots, with cuts per minute and shot lengths (median, shortest, longest)
   - how long the first shot holds (the hook)
   - loudness, and how much near-silence there is
   - a sheet with the first frame of each shot, and a sheet of the first 3 seconds

   Look at the sheets for:
   - text: where it sits, how much, its style
   - transitions
   - colour
   - structure: how it opens, the order of things, how it ends

   Transcribe it if speech matters (narration, interviews, a talking head).
3. **Write a short style brief.** Cover:
   - the structure, the length and the pacing, in numbers
   - the hook
   - text: where, how much, the style
   - sound: music, speech or natural sound
   - transitions, colour and aspect
   - what makes it distinctive
   - what you couldn't tell
   Where the examples disagree, say so rather than averaging them.
4. **Show it and ask: "Is this what you like about them?"** Their corrections go into the brief. Ask for one or two
   more examples if:
   - you can't explain what makes them work
   - they contradict each other
   - the user says you've missed it
   Specific moments help more than more videos.
5. **Save the brief** in `taste-profile.md` under "References and style brief". It overrides the long-form defaults for
   this project. Pick the frame and length from it.
6. **Expect a few rounds.** The first cut of a new type is a draft to react to. Each review, and the user's own edits
   (`learn`), tighten the brief.
