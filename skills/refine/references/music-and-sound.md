# Music and sound

## When to use music

Not everything needs music. Where a place's own sound carries it, let it.
- **Natural sound, no music:** street scenes with character (vendors, traffic, a market setting up). Busy local
  restaurants and food halls where the crowd, the cooks and the kitchen are the point. A process with good sound
  (whisking, pouring) can play almost like ASMR. Usually one such stretch per day or chapter, 15–40 s.
- **Music:**
  - openings
  - chapter cards
  - travel between places
  - quiet cafés and galleries
  - mall walks: cover a shop's own music, which can trigger copyright claims
  - views
  - the end of a day or the film
- **A muted stretch always gets music.** If speech forced you to mute a few seconds or more, put a song under it, even
  on a street. Silence there sounds broken.
- **How to switch:** the song fades out over at least 1.5 s, ending on the cut where the natural-sound stretch starts,
  and comes back on a cut with a 1–1.5 s fade in. Never cut music mid-shot.

## Levels

- **Music sits low, under the clips' own sound.** It's a bed, not the lead.
- **Even out quick cuts.** A loud street next to a quiet café is jarring. Measure each shot's integrated loudness (LUFS)
  and set its volume from it:
  `volume = base × 10^((target − LUFS) / divisor)`
  with target −21 LUFS and divisor 20 for a full match or 40 for a gentle, half-strength match. Cap at 2.0. A
  near-silent shot can't be lifted without hiss. Raise the music there instead.
  - **base** is the level a clip at the target loudness should sit at. **1.0 when the clips' own sound carries the
    film** (a first cut, or a natural-sound stretch with no music). **About 0.3 under music**, so the music leads.
    A new clip in Edits starts at 1.0; base 0.3 with no music makes the whole film about 10 dB too quiet.
- Then check the rendered mix in short windows. Aim for about 2 dB between neighbouring shots in a montage.
- Natural-sound stretches should sit about 1–3 dB under the music sections.

## Cuts and speech

- **Transcribe whole clips.** Transcription tools invent words on short snippets.
- **Cut on the quietest moment between words** (or between footsteps and hits) within about ±0.25 s of the planned cut.
  Some apps' MCP can find that point for you.
- **Give every clip's audio a tiny fade in and out** (about 2 frames) so shots hand over without a click. Audio only;
  the picture stays a hard cut.
- **Companion speech:** mute it, or better, swap in a shot without speech. A muted shot is a dip in an even mix.

## Music library

- **For YouTube, use royalty-free tracks.** In-app "licensed" music may be cleared only for that app's own platform,
  and can trigger copyright claims elsewhere. Check each track's licence if the app reports it.
- Royalty-free tracks are mastered at different levels. Match them by ear or by output level, not by their volume
  numbers.
- **Music doesn't move when the picture changes.** After any edit that changes length, re-fit every section to its
  scene: start on the scene's first cut, keep natural endings. Then re-fit the last song so it ends with the film.
