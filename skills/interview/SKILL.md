---
name: interview
description: Optional. Builds the user's taste profile for Video Edit Copilot up front through a short conversational interview (references, structure, pacing, what deserves time, captions, music and sound, colour, phone footage, voiceover, privacy, delivery). Also the question bank that refine draws on. Use when the user runs /video-edit-copilot:interview, would rather describe their taste before seeing a cut, starts a new series, or says the edits don't feel like theirs.
---

# Taste interview

The taste profile is what makes the copilot edit like the user instead of like a template.

**This interview is optional.** By default the copilot makes a first cut with almost no questions (`first-cut`), then
asks only what each refinement needs, as choices on what the user has just watched (`refine`). Most of the profile is
written by `learn`, from the user's own edits. Run the full interview only when the user would rather describe their
taste before seeing anything, or is starting a new series. Either way, the batches below are the question bank: `refine`
asks from the batch that matches the area being worked on.

If you do run it, keep it short (10–15 minutes), concrete, and easy to answer.

## How to run it

- Ask in **small batches** (2–4 questions at a time), in the order below. Wait for answers.
- Offer **choices with a recommended default** wherever you can. Most people find picking easier than describing taste
  ("A: long holds on food, B: quick throughout, C: depends on the place").
- Ask for **real examples**: two or three videos they love and *what exactly* they like in each. Use the references only
  to understand the style. Never copy their content, wording or identity.
- If they don't know, write "not decided: learn from edits" and move on. Don't push.
- Ask about facts (people's names, places) only when needed, and never put a name on screen without confirming it.

## Batches

1. **The video:**
   - What is it, and who is it for?
   - Long-form, short-form, both, or another type (`references/video-types.md` in `refine`)?
   - Platform, aspect ratio, target length.
   - One long film, or a series of episodes (by day, place or topic)?
2. **References:**
   - Two or three videos they'd like theirs to feel like, and why. Study them with "Learning a new type from examples"
     in the `refine` skill's `references/video-types.md`: analyse, write a short style brief, then ask "Is this what
     you like about them?". Ask for one or two more if it's still unclear.
   - Anything they dislike: hype cuts, shouting captions, music over everything, speed ramps.
3. **Structure:**
   - Chapters by day, by place, or by topic?
   - An opening montage or title?
   - Chapter cards?
   - How each place or segment should unfold. Offer the default pattern: arrive → identify → the thing itself → the
     moment → a detail → leave.
4. **Pacing:**
   - What deserves time: food, the process of making something, views, people?
   - What should be quick: walks, arrivals, transit?
   - Rough hold lengths for each.
5. **Captions:**
   - What captions are for: place names, addresses, dish names, small personal notes, context.
   - How they should sound: plain and specific is the safe default.
   - Look: font, size, position, background pill or not, animation (a quick fade is the safe default).
   - Ask for one example caption in their own words.
6. **Music and sound:**
   - Where music comes from. For YouTube, royalty-free only. In-app "licensed" tracks may be cleared only for that
     app's platform.
   - Music everywhere, or let places with good natural sound carry themselves?
   - Mute people's conversations, or keep some?
7. **Colour:**
   - Camera and log profile (from setup).
   - The conversion LUT.
   - A finishing look and its strength, or natural.
8. **Phone footage:**
   - Use it at all?
   - As short personal inserts (vertical clips in the wide frame), as stills, or as full shots?
   - Was any of it shot in log?
9. **Narration:**
   - None, their own recorded voice, a built-in AI voice, or their own cloned voice (see the voiceover skill).
10. **Privacy:**
    - Who must not be identifiable: strangers' children, licence plates, screens.
    - Any person who shouldn't appear at all.
11. **Working style:**
    - How they want to review: a decision log before building (recommended), options pages for captions (recommended).
    - What you must always ask about first.

## Write the profile

Fill `taste-profile-template.md` (in this skill's folder) and save it as `video-edit-copilot/taste-profile.md` in the
project. Write each preference as a rule with its reason where they gave one, because the reason is what lets a rule
apply sensibly to new footage. Keep their own words for anything personal. Read it back as a short summary and ask
for corrections.

End by suggesting the next step: `/video-edit-copilot:first-cut` if there's no cut yet, otherwise `/video-edit-copilot:refine`.
