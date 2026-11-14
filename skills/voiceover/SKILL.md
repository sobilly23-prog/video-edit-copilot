---
name: voiceover
description: Adds narration to a Video Edit Copilot edit in one of three modes - the user's own recorded voice (script, teleprompter, record per section), a built-in AI text-to-speech voice, or the user's own cloned voice from an outside service - with script, timing and mixing rules. Use when the user runs /video-edit-copilot:voiceover, asks for narration or a voiceover, or their taste profile asks for one.
---

# Voiceover

Narration is optional. Many personal videos work better with captions and natural sound. Read the taste profile's
**Narration** section. If it's empty, ask which mode they want, recommending "none" for calm, observational videos.

## The three modes

1. **Your own voice, recorded:** the most personal, and the safest.
   - Draft the script per section (rules below) and show it for approval.
   - Load each section's lines into the app's teleprompter if it has one. In Edits, look for teleprompter tools
     (`setTeleprompterText`, `openTeleprompter`) and voiceover recording tools (`startVoiceoverRecording`,
     `stopVoiceoverRecording`, or `recordVoiceover`).
   - The user records section by section. You place, trim and level the takes.
2. **A built-in AI voice:** quick and consistent.
   - In Edits, list the voices (`listTTSVoices`), let the user pick by sound, then apply text to speech per line
     (`applyTextToSpeech`).
   - Tell the user it's a synthetic voice, and check their platform's rules on labelling synthetic audio.
3. **Your own voice, cloned:** sounds like them without recording every line.
   - Made with an outside voice-cloning service. The user sets it up themselves with their own account and their own
     voice samples. Then import the generated audio files as audio.
   - **Only ever clone the user's own voice.** Never clone anyone else's, even if asked. Never make a voice say
     something the person wouldn't.
   - Check the platform's labelling rules for synthetic audio.

Tool names vary by app and version. Check `app-capabilities.md` and load each tool's schema before calling it.

## Script rules

- **Write like the user talks.** Use the voice from the taste profile and their own captions. Short sentences.
- **Narration doesn't repeat a caption.** Say what the picture can't show (why you came, what surprised you), not what
  it can.
- **Anything that sounds like their opinion is a draft for them to approve.**
- **Leave room:** not every shot needs words. Hero shots and natural-sound moments breathe.
- **Time each line to the shots it's about.** About 2.5 words per second is a comfortable pace. If a line runs past
  its shots, shorten the line before stretching the picture.

## Mixing

- Music dips under the voice: about 6–10 dB, with the app's ducking if it has it, otherwise volume changes with short
  fades.
- The natural sound under a narrated line drops a little too.
- Level the narration evenly across sections. Use the app's voice enhancement if it helps; check it doesn't sound
  processed.
- **Check by listening to a short render of each narrated section,** not by reading the numbers.

## Hand over

List each narrated section with its line and timing. Say which mode was used and whether anything synthetic needs
labelling.
