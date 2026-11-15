# Music and sound

Viewers forgive a cut that's a frame late. They notice at once when the sound goes silent, or a sound cuts in hard, or
the level jumps on a cut. In the film this plugin was built on, every sound problem viewers mentioned came from the
edit, not the render. So the sound check below is required, not a polish step.

## When to use music

Not everything needs music. Where a place's own sound carries it, let it.
- **Natural sound, no music:** street scenes with character (vendors, traffic, a market setting up). Busy local
  restaurants and food halls where the crowd, the cooks and the kitchen are the point. A process with good sound
  (whisking, pouring, a wok) can play almost like ASMR: raise its own sound and take the music out. Usually one such
  stretch per day or chapter, 15–40 s.
- **Music:**
  - openings
  - chapter cards
  - travel between places
  - quiet cafés and galleries
  - mall walks: cover a shop's own music, which can trigger copyright claims
  - views
  - the end of a day or the film
- **A place's own sound leads where it's the point.** In a café, the grinder, cups and the barista go at their
  loudness-matched level and the song drops to a low bed under them. It comes up only over muted shots, so those don't
  dip. If the user wants a place's own music heard (a record player, a busker), keep it, stop the song for it, and
  flag the copyright-claim risk before publishing instead of burying it.
- **A muted stretch always gets music.** If speech forced you to mute a few seconds or more, put a song under it, even
  on a street. Silence there sounds broken.
- **A place's song starts once you're inside it,** on the sign or the first interior shot, not on the way there. Carry
  the travel song through the arrival. Never change songs mid-timelapse.
- **How to switch:** the song fades out over at least 1.5 s, ending on the cut where the natural-sound stretch starts,
  and comes back on a cut with a 1–1.5 s fade in. Never cut music mid-shot. End the film on a song's natural ending,
  its fade at least as long as the picture's.
- **Draft fewer songs than you think.** A repeat visit or a quiet walk home can run on its own sound. The user's own
  music choices win: a song they removed stays removed, and once they've rearranged the music, every later re-fit
  carries *their* arrangement, never your original plan.

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
- Then check the rendered mix in short windows. Aim for about 2 dB between neighbouring shots in a montage, and **never
  more than about 6 dB across any cut** (the sound check's JUMP finding).
- Natural-sound stretches should sit about 1–3 dB under the music sections.
- Table chatter and people talking in the background go down further (about 0.15–0.2) so they don't pull focus.

## Cuts and speech

- **Transcribe whole clips.** Transcription tools invent words on short snippets.
- **Waveform cuts (required).** Every cut lands on the quietest moment within about ±0.25 s, between words and between
  footsteps and hits, never in a word or on a hit. Do it on the plan before building (`waveform_cuts.py` in the Edits
  playbook), and on the built film with a slip, which keeps each shot's place and length (`waveform_slip.py`). Slip
  your own cuts. The user's own cuts go on the review page for them to decide.
- **Frame audio transitions (required).** Every cut where the sound jumps gets a tiny audio fade (about 2 frames) on
  both sides, so shots hand over without a click. Audio only: the picture stays a hard cut. A continuous split (one
  take cut in two, the second piece picking up where the first stopped) gets no fade: the sound never jumped, so a
  fade would only make a dip. Longer fades someone chose are kept.
- **Companion speech:** mute it, or better, swap in a shot without speech. A muted shot is a dip in an even mix. The
  user's own spontaneous reaction can often stay, turned well down, rather than muted: offer it.

## Silence and dead air

**Silence is fine when it's meant:** a beat before a reveal, the end of a day, a hush the user chose. Accidental
silence is the problem. The common causes, and their fixes:
- **A title or chapter card with no sound.** A 0-volume card with no music is dead air, and so is a song that starts on
  the card with its own silent intro: 3–4 s of nothing at every new chapter. Give the card a bed: start the next song
  about 1 s before the card with its silent intro trimmed, so it's audible on the card's first frame, or let the last
  shot's own sound fade out under the card.
- **A shot muted to 0 over a sparse song.** Under a lone piano or a quiet intro, the film drops to near-silence between
  notes and each note pops in. Mute to 0 only where a steady bed covers it. Otherwise keep the shot's own sound low
  (about 0.05–0.1), or swap the shot. Never use a sparse song intro as the only sound.
- **A silent picture:** a photo, a still, a title graphic, a screen recording. Every one gets a bed, baked into a copy
  of the clip (the picture copied untouched, the same length) and swapped in place.
  - A single still takes a few seconds of the **next** shot's own sound, from just before the part of it that's used,
    at that shot's volume. It flows straight into the next shot.
  - A run of stills takes one continuous stretch of the place's own room tone (a voice-free clip from the same place;
    check its transcript), about 10 dB under the music.
  - Bake it: `ffmpeg -i still.mp4 -ss <s> -t <length> -i next.mp4 -map 0:v -map 1:a -c:v copy -c:a aac -shortest
    still_bed.mp4`. In Edits, swap with `replaceElementMedia` (it keeps the clip's place and length), then set its
    volume and fades.

## The sound check (required)

Run it after the first build, after every review round, after every pass of the user's own (their splits and trims
add cuts, and music doesn't ripple, so sound seams move), and on the exported file before publishing.
1. **Render the stretch you changed** (in Edits: `render_audio.py`), or use the exported file.
2. **Scan it:** `sound_scan.py <file> --start <s> --snapshot <snapshot.json>`. It lists DROPOUT, QUIET, CUT-IN,
   CUT-OUT and JUMP, each placed ON a cut (the edit caused it) or MID-SHOT (the source or the render).
3. **Re-run both techniques:** `audio_fades.py "<title>" 0 <end> --check` must show zero clips with sound missing a
   fade (apply with the same command without `--check`), and `waveform_slip.py … --dry` for cuts on a loud moment.
4. **Give every finding a verdict:**
   - **intentional:** keep it, and say why in the decision log
   - **accidental:** fix it (a bed under a silent picture, a song seam, a fade, a level)
   - **unsure:** don't fix it. Flag it for the user with the timecode, what it sounds like, and the fix you'd make,
     with "now" and "with the fix" sound clips on the review page (`caption-picks`)

   A fix nobody asked for that changes how a moment feels (a bed under a still, a song moved) is flagged too, with how
   to undo it.
5. **Re-scan,** then write one line in the decision log: `Sound check: found N / fixed N / kept N (why) / flagged N`.

## Music library

- **For YouTube, use royalty-free tracks.** In-app "licensed" music may be cleared only for that app's own platform,
  and can trigger copyright claims elsewhere. Check each track's licence if the app reports it.
- Royalty-free tracks are mastered at different levels. Match them by ear or by output level, not by their volume
  numbers.
- **Check a track's first seconds before placing it.** Many start with silence or a very quiet intro. Trim that, or
  start the track earlier, so the music is audible where the picture needs it.
- **Music doesn't move when the picture changes.** After any edit that changes length, re-fit every section to its
  scene: start on the scene's first cut, keep natural endings. Then re-fit the last song so it ends with the film. Then
  run the sound check: a re-fit moves song seams.
