---
name: assist
description: A fast editor on the side. Does one specific task in the user's video app on request, especially things they don't know how to do yet or that the app's screens can't do (blur someone, restyle every caption, fix one shot, move the music, check loudness, watch an export), and explains where the control lives if they want to learn it. Use whenever the user asks for a single change or a how-to in their video app, outside a full refine round ("make all captions fade faster", "blur that face at 2:10", "how do I add a LUT", "why is the export so slow").
---

# Assist

The user is often editing in the app themselves. This skill is the colleague next to them: they say what they want
in plain words and you do it, quickly and safely, so they can stay on the story instead of learning every menu. It's
also how someone new to the app gets past the learning curve.

## How to handle a request

1. **Pin down exactly what and where.** Turn "that face at 2:10" into an element: read the project (snapshot or the
   app's element list) and find what's on screen at that time. Look at a frame before changing anything, and confirm
   if there's any doubt about which shot, caption or song they mean.
2. **Check it's safe to act:** the right project is open (check its title), and the user isn't mid-edit (the playhead
   isn't moving and nothing is playing). Take a snapshot before a change that touches more than one element.
3. **Do the smallest change that does the job,** with the app's MCP tools. One change at a time. Keep the film's
   length unless they asked to change it: to lengthen one shot, shorten its neighbour by the same amount.
4. **Check the real result:** an export frame for anything visual, a short preview render for sound or motion. Don't
   trust the tool's readback alone.
5. **Report in two lines:** what changed, how you checked it, and how to undo it (the app's undo, or the snapshot).
6. **If they want to learn it,** say where the control is in the app's screens. If there is none (exact values, bulk
   changes, tracking), say that the MCP can do things the screens can't.

## Judgement calls

| Request | Do |
|---|---|
| A clear mechanical change ("move this caption to the next shot") | Do it, then report |
| A taste call with a few reasonable answers ("make this caption better") | Offer 2–3 options, ideally on a picks page (`caption-picks`) |
| Anything personal (their opinion in a caption, a person's name, who to blur) | Ask |
| Something that would undo their own edit | Ask, and explain what it would undo |
| Something the MCP can't do | Say so, then give the exact clicks, or offer to click it with computer use if they allow it |

## What people usually ask for

These are good to offer when someone is new to the app, because the app's screens make them slow or impossible:
- **Bulk changes:** restyle or retime every caption, change every fade, set every clip's volume from its loudness.
- **Exact numbers:** a LUT at 12% strength, a caption at exactly the same position as another.
- **Privacy:** blur a person who moves through a shot, by describing them ("the man in the red jacket"), if the app can
  track objects.
- **Finding things:** every caption that mentions a word, every shot from one place, the quietest moment to cut on.
- **Checks:** caption overlaps, loudness jumps between cuts, frames from the real export pipeline.
- **Long jobs:** watch an export and report when it's done or if it stalls (see `package`).

## Learn from it

- A lesson about the app (a tool that misbehaves, a step only the screens can do) goes into
  `video-edit-copilot/app-capabilities.md`, or the app's playbook.
- A preference ("captions always fade quickly") goes into the taste profile as a candidate rule, the way `learn` does.
