# Phone footage

Most trips are shot on two things: a main camera and a phone. Phone media adds personal moments the main camera
missed. Use it the way the taste profile says (none, inserts, stills, full shots), and offer each use as an option first.

## Kinds of use

- **Inserts:** a vertical phone clip (holding the bowl, a quick look out of a window, a moment of eating) placed in the
  middle of the wide frame. It works as a personal beat between the main camera's shots. Keep them short, 3–7 s, and
  rare, or they stop feeling personal. Some apps import vertical clips at the wrong size or crop them: render the
  insert yourself onto a frame of the film's size (centred, with plain sides) if needed.
- **Stills:** photos between days or places, or a final image for the end card, centred on the frame.
- **Full shots:** horizontal phone clips can stand in for missing main-camera shots. Match their colour carefully.

## Colour (the part that goes wrong)

- **Phone clips are usually not log.** They're already in normal colour. The camera's log conversion must be kept off
  them: on phone footage it crushes the shadows and pushes the saturation too far. With adjustment layers, leave a
  gap in the conversion layer over every phone shot.
- **Phone log footage** (Apple Log and similar) needs its own conversion LUT for that phone. Check the file tags and
  a frame. Don't assume.
- **Phone photos** are often in a wider colour space (Display P3). Convert them to the video's colour space (Rec.709),
  then grade them to match the camera's look.
- Some apps render phone stills noticeably darker in the midtones than the original. Compare an export frame with the
  photo and adjust.
- **Check every phone shot against its neighbours** in an export frame before calling it done.

## Clocks

- **Phone and camera clocks rarely agree.** They can be minutes or hours apart (time zones, a camera clock never set).
  Match phone clips to the right moment by what's in the picture, not by the time on the file.
- **File-manager dates can be shifted further by sync services.** Use the date stored in the media itself.

## Same checks as camera footage

- Transcribe it and handle speech the same way.
- Trim to the part worth keeping.
- **Privacy:** phones capture more faces up close.
