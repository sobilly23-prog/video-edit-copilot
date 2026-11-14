---
name: setup
description: First-run onboarding for Video Edit Copilot. Asks what kind of video the user is making (long-form, short-form, both, or another type, learned from 2–3 of their examples) and which video editing app they have, confirms it's connected to Claude Code through an MCP server (the one hard requirement for editing), maps what the app's tools can do, inventories the footage (camera and phone), notes whether it was shot in log, checks helper tools, and creates the project's working folder. Colour grading is not part of setup; it happens once the clips are in the app. Use when the user runs /video-edit-copilot:setup, starts using the plugin, or editing fails because the app isn't connected.
---

# Setup

Two things shape everything after setup:
- **The kind of video,** which sets the defaults.
- **The app's MCP server,** the one hard requirement for editing, because it's the only way the copilot can work
  inside the user's own video app.

Settle both plainly. Everything else in setup is quick by comparison. Keep it short: the user came here to see their
footage cut, not to fill in forms.

**Ask everything in one message** (skip anything you already know):
1. **What kind of video are you making?**
   - **Long-form:** YouTube-style, several minutes and up, such as a travel vlog or a trip film.
   - **Short-form:** Reels, Shorts or TikTok, vertical and under a minute.
   - **Both:** a long film, plus shorts from the same footage.
   - **Something else:** say what, for example a wedding, an event recap, a product video or a tutorial.
2. **Is there a video you'd like yours to feel like?** Two or three links or files, and a line on what you like in each.
   - Optional for long-form and short-form.
   - **Needed for "something else":** that's how the copilot learns a type it wasn't built for.
3. Which video editing app do you use?
4. Where's your footage? Ideally one folder per day, with a sub-folder per place.
5. Any phone clips or photos you'd like to use? Where are they?
6. Was it shot in a log profile (flat, grey-looking footage, such as D-Log M, S-Log3 or Apple Log)? "Not sure" is
   fine: setup checks a frame.

Report each step as ready, missing (with the exact fix), or skipped. Setup ends by pointing to the next step.

## 1. The kind of video

Read `references/video-types.md` in the `refine` skill's folder.
1. **Record the type** in `settings.json`: `video_type` (`long-form`, `short-form`, `both` or a short description),
   `aspect` (`16:9` or `9:16`) and `platforms` (for example YouTube, Reels).
2. **Say what that means, honestly:**
   - **Long-form:** built and tested.
   - **Short-form:** sensible defaults, less testing.
   - **Something else:** the first cut will be a draft built from their examples, and it gets better with each
     review.
3. **Examples:**
   - **If they gave any, study them now** with the "Learning a new type from examples" steps in `video-types.md`:
     analyse each, write a short style brief, and ask "Is this what you like about them?".
   - **For "something else" with no examples yet:** ask for 2–3 before the first cut. Ask for one or two more if the
     brief is still unclear.
   - Save the brief in `taste-profile.md`, creating it from the template in the `interview` skill's folder if needed.

## 2. The editing app and its MCP server (do not skip)

Say plainly that the copilot was **built and tested with Instagram Edits for Mac**. Other apps can work if they have an
MCP server: the method is the same, and the app-specific parts (tool names, quirks, what needs the screen) live in one
playbook per app.

1. Look for the app's tools in this session: an MCP server whose tools edit a timeline (import media, trim, add text,
   export). Instagram Edits for Mac registers its server as `metapilot-native` by default.
2. If you find them, call one **read-only** tool to prove the connection is live (for Edits: `getCapabilities`, then
   `appState` and `title`). A server listed but refusing connections usually means the app is closed: ask the user to
   open it.
3. **Check which project is open.** Edits reopens the last project when it starts, so the user's own film may be open.
   Only read from it. Tell them the first cut goes into a **new** project, and that they'll need to close theirs first
   (to the home screen). Never close, open or save over a project you didn't create.
4. If there's no such server, stop and explain, in plain words:
   - Without an MCP connection the copilot can still sort and map the footage, plan the cut, write a decision log and
     draft captions, but it can't edit anything in the app.
   - **Instagram Edits (Mac):** Settings → Automation → Enable Automation Server. Edits shows a ready
     `claude mcp add …` command. The user copies it and runs it **themselves** in a terminal, then starts a new Claude
     Code session.
   - **Another app:** look up whether it has an MCP server (its docs, its settings, a search). As of November 2026:
     - **DaVinci Resolve 21.1 and later (Studio):** an official, built-in server.
     - **Premiere Pro, Final Cut Pro and CapCut:** only community-built servers. CapCut's community servers write
       project files that you then open in CapCut, rather than controlling the app live.
     Check before promising anything. If the app has none, say so honestly and offer planning-only mode.
5. **Never ask for, accept, print or store the app's token.** If the user pastes one into chat, tell them to rotate it
   in the app and don't repeat it.
6. If the app quits during the session, its tools drop out and can take a while to come back after a relaunch. The
   Edits helper scripts talk to the server directly and keep working.

## 3. Map what the app can do

Different apps, and different versions of one app, expose different tools. Write down what this one has.
1. Read the app's own capability or help tool if it has one. Then list the tool names by area: project, media,
   timeline, text, audio, colour, effects, analysis (transcription, shot detection, people/object tracking), rendering
   (frame capture, preview renders, export), voiceover, catalogs.
2. Note the things the MCP can do that the app's screens can't (exact numbers, bulk edits, full project reads,
   analysis). Also note the things only the screens can do. In Edits:
   - importing a .cube LUT file (once: Edits keeps imported LUTs for every project)
   - adding a song from the music library
   Those need the user, or computer use if they allow it.
3. Save it as `video-edit-copilot/app-capabilities.md` in the project. The `first-cut`, `refine` and `assist` skills
   read it.
4. If the app is Instagram Edits, load the `edits-playbook` skill: it has the tested recipes, helper scripts and known
   quirks.

## 4. Footage

Use the folders the user gives. Don't guess, and don't search the whole disk.

1. **Inventory**, read-only:
   ```
   python3 -I <sort skill folder>/scripts/inventory.py <footage folder> [--depth 2] [--json inventory.json]
   ```
   It reports:
   - clips and minutes per folder
   - formats
   - the camera each file names (DJI writes it into the file, phones their make and model)
   - the colour tags
   - where each shooting time came from
   - broken or 0-second files
2. Filename timestamps usually give the shooting order. Finder dates often don't: they can be shifted to the computer's
   time zone.
3. **If it isn't sorted by date and place, offer the `sort` skill.** Sorting chronologically, by day and then place,
   makes every later step faster, and it moves files only after the user approves the plan.
4. **Never move, rename or delete a source file** outside an approved sort plan. All other work happens on copies.
5. Many apps can only read certain folders: Edits' sandbox can't read external drives. Agree on a **working media
   folder** the app can read (for Edits, a folder under `~/Movies/`). Clips are copied there only as they're used.

## 5. Log or not (no grading yet)

Colour grading isn't part of setup. It happens after the clips are in the app (`first-cut`, then `refine`).
1. **Note the camera and whether it was shot in log.** File tags often claim Rec.709 even when the picture is log, so
   look at one frame: log is flat and grey.
2. **Mixed footage:** phone footage is usually not log and must never get the camera's conversion. Record which clips
   are log in `log_sources` (filename patterns).
   - Be careful with patterns. `_D\.MP4$` matches every recent DJI file, log or not.
   - Use a pattern only if every clip it matches is log. Otherwise leave it empty and let the first cut check frames.
3. Mention, without asking yet, that the first cut will ask whether they have their own LUT for this camera.

## 6. Helper tools

Check each and give the exact fix if it's missing:
- **`python3`**
- **`ffmpeg` and `ffprobe`:**
  - `brew install ffmpeg` is enough to start.
  - A full build adds `drawtext` (labelled sheets) and `vidstab` (stabilising): `brew install ffmpeg-full`. It's
    installed beside the plain one, not on the PATH, so add
    `export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"` to the shell profile.
- **A transcription tool:** for example the MacWhisper command line (`mw`) or `whisper`.
- **Optional: computer use,** for the few screen-only steps.

## 7. Working folder

Create `video-edit-copilot/` in the project:

```
video-edit-copilot/
  settings.json          paths, the app and camera (template below)
  app-capabilities.md    from step 3
  taste-profile.md       grows from the user's answers and edits (created by refine or interview)
  decision-logs/         one per day or section
  snapshots/             project snapshots, used to learn from the user's edits
  frames/  picks/        frame sheets and options pages
  references/            analyses of the user's example videos (when they share some)
```

`settings.json`:

```json
{
  "video_type": "long-form",
  "aspect": "16:9",
  "platforms": ["YouTube"],
  "editing_app": "Instagram Edits",
  "mcp_server": "metapilot-native",
  "project_title": "",
  "footage_root": "",
  "phone_media": "",
  "work_media": "",
  "camera": "",
  "log_profile": "",
  "log_sources": [],
  "log_lut": "",
  "app_lut_preset": "",
  "finishing_lut": "",
  "finishing_strength": 0.12
}
```

- `video_type`, `aspect` and `platforms` come from step 1.
- `camera` and `log_profile` come from the inventory and the user, for example "DJI OsmoPocket3" and "D-Log M".
- `log_sources` holds filename patterns for clips shot in log (see step 5).
- `log_lut` (a .cube file) or `app_lut_preset` (the app's built-in conversion) is filled in when the first cut asks
  about colour.

## 8. Finish

Summarise in a short table:
- video type, and any style brief from their examples
- app and connection, and the open project
- capabilities file
- footage and phone media
- log or not
- tools
- working folder Then point to the next step:
- `/video-edit-copilot:sort` if the footage isn't sorted by date and place
- `/video-edit-copilot:first-cut` otherwise

Mention that `/video-edit-copilot:interview` is there for anyone who'd rather describe their taste up front.

## Done when

- The video type is recorded, and for a type that isn't built in, a style brief from the user's examples is confirmed
  in `taste-profile.md` (or the user knows it's needed before the first cut).
- The app's MCP connection answered a read-only call. If there's no MCP server, the user knows editing isn't possible
  and what planning-only mode offers.
- `app-capabilities.md` and `settings.json` exist, with the footage folder, working media folder, camera and log notes.
- Nothing in the user's app or footage was changed.
