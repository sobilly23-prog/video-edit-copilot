---
name: learn
description: Learns the user's editing taste from their own revisions. Snapshots the project, diffs it against the copilot's hand-over, works out the rule behind each change (trims, extensions, reorders, deletions, caption rewrites, music moves), writes the rules with reasons into the taste profile, applies the user's option picks and notes, and repairs what their edits left misaligned without undoing anything. Use when the user runs /video-edit-copilot:learn, says they've finished reviewing or editing, sends picks like "1B, 2A", or sends review notes.
---

# Learn from revisions

This is the core of the copilot. People are better at **showing** their taste than describing it: a trim says more
than a paragraph. So the copilot treats every review as evidence, works out the rule behind each change, and writes
it down with its reason. After a few rounds the cut starts to look like theirs.

## 1. Read what they changed

1. Check the user is idle in the app (the playhead isn't moving and nothing is playing for about a minute) and that
   the right project is open.
2. Snapshot the project into `video-edit-copilot/snapshots/` and diff it against the hand-over snapshot (the
   playbook's `snapshot.py` and `diff_edits.py` for Edits). The diff covers:
   - **Clips:** trimmed or lengthened (which edge, by how much, what's now in or out of the shot), moved, removed,
     added, volume changed.
   - **Captions:** reworded (keep the exact before and after), retimed, deleted, added by them.
   - **Music:** moved, trimmed, removed, faded, volume.
   - **Colour and effects:** layers added, removed, moved.
3. **Look at the frames around each change.** "Shortened by 3 s" tells you nothing until you see that the 3 s were
   someone walking in.

## 2. Turn changes into rules

For each change, ask: what would make someone do this? Then write it down at the right strength:
- **A pattern** means the same kind of change in two or more places, or the user said it outright. It becomes a
  **rule**.
  Example: arrivals cut to their last 2–3 s three times → "Arrivals are short: start when the sign or door is in
  frame."
- **A one-off** is noted as a **candidate** and confirmed at the next one, not generalised yet.
  Example: one food shot lengthened → "Candidate: food shots run longer than I cut them."
- **A correction of fact** (a name, a spelling, a dish) fixes that caption, and becomes a working rule ("check drink
  names against the menu"), not a taste rule.
- **A change to wording** is the most valuable taste signal: compare the before and after to learn the user's voice.
  For example, they removed adjectives, added a personal comparison, or cut a narrating line.

Write each rule into `video-edit-copilot/taste-profile.md` under **Learned from revisions**:

```
### <date> · <short name>
- Seen: <what they changed, briefly, with counts>
- Rule: <one line>
- Why: <their reason if they gave one, otherwise your best reading, marked as a guess>
- Example: <one concrete case>
```

**Keep taste and mechanics apart.** Lessons about the app (a tool that misbehaves, a step that needs the UI) go in
the app playbook or `app-capabilities.md`, not the taste profile.

## 3. Apply their picks and notes

- **Option picks** come back like `1B, 2A, 5C`, numbered in the order of the picks page.
- **Their own notes beat a pick.**
- **Words in quotes** ("more like a snack") mean "help me write this". Write the final line yourself and show it.
- **"No line here"** means delete it.
- **Apply the picks, then check:** no overlaps, the minimum time on screen, each caption on its shot. Report the final
  wording.

## 4. Repair, never revert

Their edits are the new baseline. Never put back something they removed, re-lengthen something they trimmed, or
reword something they wrote. But their edits often leave things out of line that they didn't intend:
- **Music doesn't move** when picture changes length. Re-fit each section to its scene, from a snapshot taken when the
  music was right. If they rearranged the music themselves, their arrangement is the one to carry forward.
- **Colour or effect layers that span a change don't stretch.** Re-fit them, then check none sits over the wrong shots.
  Phone footage stays out of the camera's log conversion.
- **Captions can drift or vanish** with a trim. Re-seat them on their shots. Ask before restoring a deleted one.
- **The last song should end with the film.**
- **App artefacts:** a 1-frame sliver left by a trim, or a replaced clip reverted by an undo. Flag them. Don't delete
  their pieces. Re-apply your own swaps if they reverted.
- **Sound seams move.** Their splits and trims add cuts with no audio fade, and moved music can leave dead air or a
  sound cutting in. Re-run the sound check (`music-and-sound.md` in `refine`): add the missing 2-frame fades (that's
  a mechanical repair), slip only your own cuts, and put anything about their own cuts or any silence you're unsure
  of on the review page for them.

## 5. Apply the new rules forward

Apply new rules to the parts the user hasn't reviewed yet. If a rule would change something they already reviewed,
ask first. Then re-verify (export frames, caption check, the sound check) and snapshot again: that's the new
"before".

## 6. Tell them what you learned

A short list: each new rule in one line, any candidates, and anything you repaired. Ask them to correct any rule you
read wrongly. A wrong rule repeated across a whole film costs more than asking.

## When to act, offer, or ask

| Situation | Do |
|---|---|
| Mechanical repair after their edit (music, layers, caption timing, missing audio fades) | Act, then report |
| A taste call with a few reasonable answers (wording, how long to hold, which shot) | Offer options on a picks page |
| Anything personal (a line that sounds like their opinion, someone's name, a privacy call) | Ask |
| A rule that would change something they already reviewed | Ask |

## Done when

- Every change in the diff is explained as a rule, a candidate, a fact fix, or "not sure: asked".
- Nothing the user did was reverted. Repairs (music, layers, caption timing) are listed.
- The taste profile is updated, a new snapshot is saved, and the user has the short list of what was learned.
