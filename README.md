# Video Edit Copilot

A Claude Code plugin that gets you from a drive full of clips to a first cut you can watch, fast. Then it stays next to you in your own video app, for as far as you want to take it.

It isn't an auto-editor. Think of it as a storyboard and a first draft, plus a quick editor on the side. It does the slow parts: sorting and watching every clip, converting the colour, assembling a rough cut, and redoing the mechanical work every time you change something. You stay the director. You can stop at the first cut and finish it yourself, refine a few things together, or go all the way to an upload-ready film with thumbnail tests.

---

## Why I made this

I came back from a three-week trip with hours of footage and no time to edit it. Then a friend told me that Instagram's Edits app now has a desktop version for Mac with MCP support, which means Claude can work inside it. I decided to try it out, with Claude Code connected to Edits on my Mac.

Over a few days I edited a 30-minute film, with Claude as my assistant. Three things surprised me:
- **How much the early steps helped the storytelling.** With the footage sorted into a folder per day and place, every clip on one page, the colour converted and a rough cut in hand, I could see the story long before I'd have found it scrubbing through clips.
- **How much faster it is with someone who knows the app.** I could ask for things I didn't know how to do in the editor (blur a face that moves through a shot, change every caption at once) and get on with the story.
- **That the edit kept getting more like mine.** Day 1 took seven rounds of corrections. By the end of the first week of editing, a review of the whole film was a page of notes, and the notes kept getting smaller. Every correction was saved with the reason behind it.

The first version of this plugin started with a 15-minute questionnaire about your taste. This one flips that around: it shows you a first cut, then asks how you'd like to refine it. It's much easier to say what you want once you've watched something.

---

## How it works

| Stage | What happens | You |
|---|---|---|
| **1. Sort and see** | A one-page map of your footage: a strip of frames for every clip, in the order you shot it. If your clips aren't sorted, it proposes a chronological layout: place (from your itinerary), then day, then category (food, coffee, B-roll, sights: rename or add your own) and place. It moves nothing until you approve the plan, and keeps a full undo. | Share your itinerary, look through the map, name the places. |
| **2. First cut** | Offers a quick preview first (one day cut to a minute or two) so you can see the style before trusting it with more. A few short questions, then a rough cut in a new project in your app: best moment of each scene, in order, sound evened out, working labels. Then colour: your own LUT for your camera, or your app's preset. | Watch it. |
| **3. Refine, as far as you want** | Asks where to take it next (story, pacing, captions, music, phone footage, voiceover, privacy), with choices based on what you've just watched. Proposes, builds, checks real export frames, hands back. | Pick a direction, or edit in the app yourself. It learns from your changes. |
| **Any time: assist** | Do one thing in the app for you, especially things you don't know how to do yet or that the app's screens can't do. | Ask in plain words. |
| **4. Package** | Last checks, watches the export, checks the file, then the upload kit: title options, thumbnails built from your own frames, an A/B test plan, a description with chapters and map links, tags, end screen. | Choose, upload. |

---

## What kind of video

Setup asks first, because it sets everything after it.

| You're making | What to expect |
|---|---|
| **Long-form** (YouTube-style, several minutes and up): a travel vlog, a trip or event film | What it was built and tested on. |
| **Short-form** (Reels, Shorts, TikTok: vertical, under a minute) | Ready-made defaults: one promise per short, a hook on the first frame, quick cuts with one hero hold, text kept clear of the app's buttons, and a per-shot reframe from landscape footage (never a blind centre crop). Less battle-tested than long-form. |
| **Both** | The long film first, then 3–5 shorts cut from it, each linking back. |
| **Something else** (a wedding, an event recap, a product video, a tutorial…) | It learns your style from **2–3 example videos** you'd like yours to feel like, plus a line on what you like in each. It measures each one (shot lengths, cuts per minute, how long the opening holds, loudness), looks at the frames, and writes back what it thinks makes them work. Then it asks if that's right. If it can't tell yet, it asks for one or two more, or for the exact moments you mean. The first cut of a new type is a draft. It gets closer with every review. |

---

## What it won't do

- **Pick your story.** It proposes; you decide.
- **Touch your original footage without asking.** Editing works on copies. The one exception is sorting: it moves files into the folders you approved, inside your footage folder, never renames or deletes anything, and keeps an undo log.
- **Work while you're using the app.** It waits until you've stopped clicking, and never opens a different project over yours.
- **Undo your edits.** Your changes are the baseline it learns from.
- **Put words in your mouth.** A caption that sounds like your opinion is offered as a draft for you to approve or rewrite.
- **Ask for or show your app's connection token.**

---

## What you need

| | |
|---|---|
| **Claude Code** | In the terminal or the Claude desktop app's Code tab (a local session; cloud sessions don't load plugins from your machine). |
| **A video app with an MCP server** | **This is the one hard requirement for editing.** MCP is how Claude talks to the app. Without it, the copilot can still sort your footage, map it and plan the cut, but it can't edit anything. **Built and tested with Instagram Edits for Mac** (Settings → Automation → Enable Automation Server). Setup asks which app you use. If yours has an MCP server too, setup maps its tools; if it doesn't, setup says so up front. As of November 2026, DaVinci Resolve 21.1+ (Studio) has an official built-in server; Premiere Pro, Final Cut Pro and CapCut have community-built ones. |
| **Python 3 and ffmpeg** | For footage maps, frame sheets, loudness checks and renders. `brew install ffmpeg` is enough; `brew install ffmpeg-full` (then add it to your PATH) adds text on preview sheets and stabilising. |
| **A transcription tool** | To find speech in your clips, for example the MacWhisper command line or Whisper. |
| **Google Chrome (or Chromium)** | Only for rendering thumbnails. |
| **Your footage** | Sorted or not. Sorted chronologically works best (place, then day, then a folder per place you visited): those names become the first guess at labels. Phone clips and photos can sit in their own folder. Your itinerary helps, in any form. |
| **Optional: a conversion LUT for your camera** | If you shoot in log (D-Log M, S-Log3, Apple Log…), your camera maker's official LUT usually looks better than an app's built-in preset. The copilot helps you pick and uses your app's preset if you don't have one. |
| **Optional: computer use** | A few app actions have no MCP tool (in Edits: importing a LUT file the first time, adding a song from the music library). The copilot can click those for you if you allow it, or tell you exactly what to click. |

---

## Install

**From GitHub** (Claude Code, in any session):

```
/plugin marketplace add sobilly23-prog/video-edit-copilot
/plugin install video-edit-copilot@video-edit-copilot
/reload-plugins
```

**From a folder or `.zip`:** unzip it somewhere you'll keep it, then:

```
/plugin marketplace add ./video-edit-copilot
/plugin install video-edit-copilot@video-edit-copilot
/reload-plugins
```

Use the real path to the unzipped folder. Start it with `./` or a full path, otherwise Claude Code reads it as a GitHub name. Once installed, it also shows up in the desktop app (**+** → **Plugins**). If you installed version 0.2 from a folder, remove it first: the marketplace was called `video-edit-copilot-local` then.

**To try it once** without installing:

```
claude --plugin-dir ./video-edit-copilot
```

## Connect your video app (once)

For Instagram Edits on Mac:
1. Open Edits → **Settings** → **Automation** → **Enable Automation Server**.
2. Edits shows a ready-made `claude mcp add …` command. Copy it and run it **yourself** in a terminal. It contains a private token, so don't paste it into a chat.
3. Start a new Claude Code session so the app's tools load.

For another app, follow its own MCP instructions, then run setup (below). It will check what the app can do. The copilot was built on Edits, so other apps may need a few things done by hand until they have their own playbook.

---

## First run

| Step | Command | What happens |
|---|---|---|
| 1 | `/video-edit-copilot:setup` | Asks what kind of video you're making (and studies your example videos if you share some), then which app you edit in, and checks its connection, then lists what its tools can do. Inventories your footage (which camera, how many minutes, any broken files), notes whether it's log, and checks your helper tools. No colour grading yet. |
| 2 | `/video-edit-copilot:sort` | The footage map, and a chronological layout (place, day, category, place) if your clips aren't sorted. |
| 3 | `/video-edit-copilot:first-cut` | A quick preview or a fuller rough cut in a new project, then colour with your LUT or the app's preset. Start with one day if it's a long trip. |
| 4 | (you) | Watch it. Then say where to take it, or edit it in the app yourself. |
| 5 | `/video-edit-copilot:refine` | One direction at a time, as far as you want. After your own edits: `/video-edit-copilot:learn`. |
| any time | `/video-edit-copilot:assist` | Or just ask: "make every caption fade faster", "how do I add a LUT?" |
| last | `/video-edit-copilot:package` | Export, thumbnails, A/B test plan, description and upload settings. |

Prefer to describe your taste before seeing anything? `/video-edit-copilot:interview` is still there: about 15 minutes of questions that write your taste profile up front.

Your taste profile, decision logs and project snapshots live in a `video-edit-copilot/` folder inside your project, so each series can have its own taste.

---

## How it learns from your revisions

This is the part I'd tell anyone about. It's the reason the edit got closer to mine instead of staying generic. You can refine by talking to it, by picking options, or by just editing in the app yourself: it learns from all three.

- **It learns from what you do, not just what you say.** Before handing a cut over, it saves a snapshot of the whole project: every clip, caption, layer and timing. After your pass it compares the two and sorts every change: trimmed, lengthened, moved, deleted, caption reworded, music moved.
- **Every change becomes a rule with a reason and an example.** "They shortened every arrival and let the food shots run the whole take" becomes *transit is quick, the subject gets time*. The reason matters: it lets the rule apply sensibly to footage it hasn't seen.
- **Options instead of open questions.** For captions and close calls it makes a page with a thumbnail and a few options for each, and you answer like `1B, 2A, 5C`. Your notes beat its options. Words in quotes mean "help me write this".
- **Taste and mechanics are kept apart.** Your preferences go in the taste profile. Lessons about the app (its quirks, what can break) go in a separate playbook, so they never get mixed up.
- **It never undoes you.** If your change conflicts with a rule it wrote, your change wins and the rule gets rewritten.

Some of the rules it ended up with for me, which are a good starting point for most personal videos:
- **Cut when the action finishes**, not mid-gesture: the pour lands, the hand takes the receipt.
- **Arrivals and walks are quick. What you came for runs as long as the shot stays good.**
- **Tell each place in the order the viewer would live it:** arrive → look around → order → it arrives → first taste → wide of everyone → leave.
- **Bridge every move between places** with a short line ("Across the road to the night market"), so the viewer always knows where you're going.
- **One caption per idea.** Name things plainly and precisely. Never describe what's already on screen.
- **Not everything needs music.** Where a place's own sound carries it, let it.
- **Even out the sound across quick cuts.** A loud street next to a quiet café is jarring.

---

## The app's MCP can do more than its screens

Connecting through MCP isn't only a faster way to click buttons. If you're new to an editing app, it gets you past the learning curve: you say what you want and it does it, and tells you where the control lives if you want to learn it. And the app's MCP often exposes things its own interface doesn't. In Edits, for example:
- **Exact numbers where the app has no control,** such as a colour LUT at 12% strength with no slider for it.
- **Changes at scale,** such as switching every caption in a 30-minute film to a quicker fade in one pass.
- **Reading the whole project:** every clip, caption and layer with exact timings. That's what makes learning from your edits possible.
- **Checking the real result:** true export frames and short renders, before exporting anything.
- **Sound analysis:** loudness per shot, and the quietest moment between words to cut on.
- **AI analysis:** transcription, shot detection, finding people and faces, following an object you describe in words.
- **Full catalogues** of effects, transitions and text animations, including some not shown in the panels.

What's available depends on your app and its version. Setup lists what yours has.

---

## Thumbnails and A/B testing

Packaging is where a lot of the work pays off or doesn't, and the only way to know what your audience clicks on and keeps watching is to test it. The `package` skill:
- **Builds thumbnails from your own film:** full-resolution graded frames, your film's title font and colour, rendered at 1280×720 and checked at the size they show in a phone feed.
- **Tries different ideas, not small tweaks:** a single beautiful shot with a person, the classic three tall panels, a shot without a face.
- **Plans the test so it teaches you something.** YouTube's Test & Compare runs up to three thumbnails and keeps the one with the most watch time. Change one thing between versions and keep the title text the same, so the result answers a real question: does a face help? Does one shot beat three panels?
- **Remembers the result** in your taste profile, so your next video starts from what won.

It also writes title options, a description with chapters and a map link for every place, tags, an end screen plan and the upload settings, all on one page you can copy from.

---

## Mixing in phone footage

Most trips get shot on two things: a main camera and a phone. The copilot can bring your phone clips and photos into the same film:
- **Phone moments as inserts.** A vertical clip (the bowl in your hand, a quick look out of a window) sits in the middle of the wide frame. It works as a personal beat between the main camera's shots. Each one is offered as an option first, not dropped in silently.
- **Photos as stills,** for example between days or places.
- **Colour that matches.**
  - Phone clips usually aren't shot in log, so the camera's log conversion is kept off them. Put on phone footage, it looks crushed and oversaturated.
  - Phone log footage gets its own conversion.
  - Photos are converted to the video's colour space and graded to match the camera.
  - It checks a phone shot against its neighbours before calling it done.
- **The two clocks rarely agree.** Phone and camera timestamps are often minutes or hours apart, so it matches phone clips to the right moment by what's in the picture, not by the time on the file.
- **The same checks as camera footage:** speech is found and muted or left out, and long clips are trimmed to the part worth keeping.

Tell setup where your phone media lives, and say how much you want it used when you refine.

---

## Voiceover (optional)

Ask for narration when you refine (or answer it in the interview). Three ways:
1. **Your own voice, recorded.** It drafts a short script per section from the decision log, puts it in the app's teleprompter, and you record it section by section.
2. **A built-in AI voice.** Edits has text-to-speech voices the copilot can apply.
3. **Your own voice, cloned,** made with an outside voice service and imported as audio.

Rules it keeps:
- Only ever clone **your own** voice.
- Check your platform's rules on labelling synthetic audio.
- Narration never repeats a caption.
- Music dips under the voice.
- Each line is timed to the shots it talks about.

---

## Making it yours

- **Your taste profile is a plain text file** in your project. Read it, edit it, delete rules you don't agree with.
- **It grows as you go.** The first cut uses sensible defaults. Each refine round adds the answers you gave, and every pass you make in the app adds rules learned from your changes. After a few rounds it holds your real preferences: how long a shot of food runs, how your captions sound, where music goes, which thumbnails win.
- **It covers:**
  - the kind of video, and videos you love and why (with a style brief from them)
  - how you structure a video (by day, by place, by topic)
  - pacing
  - what deserves time
  - caption voice, look and placement
  - music and sound
  - colour
  - phone footage (whether and how to use it)
  - privacy (who shouldn't be identifiable)
  - narration
  - packaging (titles, thumbnails, test results)
  - how far you usually take it
- **Not a travel vlogger?** The method is the same for any video. Tell setup what you're making, and share 2–3 examples of the style you want.

---

## What to expect, honestly

- **The first cut is a draft.** It's built to be watched and reacted to, not published.
- **Refining takes the longest the first time.** That's where most of your taste gets captured.
- **It makes mistakes, and the review loop is where they get caught.** Mine included:
  - a wrong name in a caption
  - captions that narrated the obvious
  - fades that were too slow
  - a meal shown out of order
  - an app readback that said something had moved when it hadn't
  - a face I'd asked to blur, still visible in one more shot of the same scene

  That's why it checks real export frames before calling anything done, and rescans every shot of a scene before the export.
- **Exports take a while.** A 30-minute 4K film took about two hours in Edits, and twice that when the display went to sleep. Keep the display on, and keep any external drive plugged in.
- **Long sessions are normal for a long film.** It keeps decision logs and notes as it goes, so the work survives a fresh session.
- **Music:** for YouTube, use royalty-free tracks. In-app "licensed" music may only be cleared for that app's platform.

---

## What's inside

```
video-edit-copilot/
  .claude-plugin/
    plugin.json            the plugin's name and version
    marketplace.json       lets you install it from GitHub or this folder
  README.md                this file
  CHANGELOG.md             what changed in each version
  LICENSE                  MIT
  skills/
    setup/                 the kind of video (+ example-video analyser), the app and its connection, footage inventory, log or not, helper tools
    sort/                  footage map + chronological sorting by place, day and category, with undo (3 scripts)
    first-cut/             a quick preview or rough cut with almost no questions, then colour
    refine/                choose a direction → decision log → build → verify → hand over
                           (+ the decision log template, and references on video types, craft, captions, music, phone footage)
    learn/                 compare your edits, update the taste profile
    assist/                one task at a time in the app, on request
    caption-picks/         options pages for captions and close calls (+ page generator)
    package/               export checks, upload kit, thumbnails and A/B test plan (+ thumbnail renderer)
    interview/             optional up-front taste interview (+ the taste profile template)
    voiceover/             the three narration modes
    edits-playbook/        Instagram Edits specifics, 14 helper scripts (incl. the cut builder), colour recipe, known quirks
```

---

*Made by Billy So, from editing my own travel film with Claude Code and Instagram Edits.*
