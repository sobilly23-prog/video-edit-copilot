# Colour recipe (Edits)

The goal: log footage converted properly, an optional gentle look on top, and phone footage left out of the camera's
conversion. Colour comes **after** the clips are in the app (see `first-cut`), not during setup.

## Choosing the conversion LUT

Pick by **log profile**, not just by camera name. Profiles with similar names are different curves: D-Log M, D-Log and
D-Log2 (DJI), S-Log3 (Sony), Apple Log and Apple Log 2, V-Log, F-Log. A LUT for the wrong profile looks wrong, however
close the name.

1. **Find the camera and profile.** Most cameras write their model into the file. In DJI files, ffprobe's
   `format.tags.encoder` reads like `DJI OsmoPocket3`. Ask the user which profile they shot in if you can't tell, and
   check a frame: log looks flat and grey before conversion.
2. **Prefer the camera maker's official conversion LUT** for that profile, from the maker's download page (ask before
   downloading anything). Makers sometimes ship one LUT under several camera names. For example, in late 2026 DJI's
   Pocket 3 and Osmo Nano D-Log M to Rec.709 files were byte-identical. Hash the user's LUT files first, and count
   identical files as one candidate.
3. **App presets are the fallback.** Edits has built-in conversions for common log profiles (16 in the version tested,
   including DJI D-Log M, Sony S-Log3, Apple Log and Fuji F-Log). They're convenient, but they're not always the
   maker's LUT. In testing, Edits' "DJI D-Log M" preset clipped whites on Pocket 3 footage where DJI's own LUT didn't.
   - **If the user has the official LUT, recommend it over the preset.**
   - If they have nothing, use the preset and let them adjust from there.
   - Either way, check it on frames.
4. **Compare when in doubt.** Render the same 3–5 frames with each real candidate (ffmpeg `lut3d` for .cube files,
   `captureFrame` for the app's preset). Put them side by side and let the user pick.

## Project settings first

- For log footage from cameras that record 10-bit, a new Edits project may default to HDR. Set the project to **SDR**
  (`setProjectDynamicRange`) and the canvas aspect ratio and frame rate (`setCanvas`) right after creating it, unless
  the user wants HDR. Then leave the user's settings alone.

## Two adjustment layers spanning the timeline

1. **Conversion (bottom layer):** `addAdjustmentLayer` with `kind: "adjust"`, spanning the whole cut, holding the
   conversion LUT at 100%.
2. **Finishing look (layer above):** an optional creative LUT at low strength, about 10–15%, set with
   `updateCatalogItem` (the UI has no strength slider). It always goes on top of the conversion, never on raw log.
3. **Order matters:** an adjustment layer affects what's below it, and new layers go on top. Add the conversion layer
   first. A conversion piece may sit on a higher track only where no finishing-look piece is below it.

## Applying the LUT

- **App preset:** `applyLUT` with the preset's name (`listCatalog` kind `lut`) on the selected adjustment layer. No
  screen needed.
- **A .cube file:** imported LUTs aren't in the tool catalog, so this needs the screen once.
  1. Select the adjustment layer. It must be **visible**: a hidden layer silently ignores the import.
  2. In the Adjust panel's LUT tab, click Import LUT, and pick the file in the system file picker. Row selection in the
     picker may need full-screen control (computer use), or the user does it.
- **Edits keeps imported LUTs for every project.** It stores them in its own container (`MCECustomLUTs/` plus
  `lut_manifest.json`).
  - After the first import, any project's LUT tab lists it, and **one tap** applies it: no file picker.
  - **Don't import the same file again:** each repeat adds a copy named "… 2", "… 3" and so on.
  - To clean up copies, check which `.lutpk` file each project's `Timeline.db` references before removing anything,
    and ask the user first.
- **Cloning an existing layer piece keeps its LUT**, so further pieces need no new tap.
- **Readback:** `getElement` on the layer reports an imported LUT (`hasLUT`, `lutFile`, `effectDisplayName`). Check it
  after the user taps.

## Gaps and cut-outs

- **Phone clips and black cards:** leave a gap in the conversion layer over every phone shot (they're not log) and
  stop it at an end card made from a photo. Black stays black, so black chapter cards can stay under it.
- **Finishing look off** over shots where it hurts: bright daylight on faces, or very dark interiors. Split the layer
  and remove the piece.
- **After anyone's edits,** check the layer pieces still sit on the right shots. Pieces that span an edit don't
  stretch, and an app-side ripple delete can move pieces onto other tracks.

## Checking

- Judge colour on **export frames** (`captureFrame`) or in the app's viewer. Other previews can be stale after grade
  changes.
- Look at the brightest shots (white plates, sky, shop lights): clipped whites mean the wrong conversion or a preset
  that's too strong.
- Phone stills can render darker in the midtones than the original photo. Compare and adjust.
- Every phone insert should sit comfortably next to its neighbours.

## Per-clip fixes

`setColorGrade` on a clip for small corrections, only when needed: exposure, contrast, highlights, shadows,
temperature, tint and similar. Ranges differ between parameters, so check the schema.
