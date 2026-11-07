# v1 "Meet Flop, Our Robot" — draft notes

**Draft:** `draft.mp4` (1920x1080, 46.5 s, no voice yet, placeholder captions). The narration lines are in
`draft.srt` and also as a subtitle track you can switch on in the player, so you can read along at the planned timing.

## Generation (Runway Gen-4.5, image-to-video, 5 s, 1280x720)
8 takes, **480 credits ($4.80)**. Balance went from 4,248 to 3,768. Seeds and task ids are in `runway_log.json`.

| Shot | Kept | Why |
|---|---|---|
| 1 Cranebot waves at Flop | **take 2** | Big, clear wing wave and the beak opens like it's talking. Flop wiggles a little "hello" (the prompt asked it to stay still, but it reads as friendly). Take 1's wave is barely visible. |
| 2 Flop rolls right | **take 1** | Clean roll with wheels spinning; take 2 is almost identical. |
| 3 Arm lifts the bag | **take 2** | Slow, steady lift. Take 1's arm swings backward past vertical (looks glitchy). |
| 4 Cranebot blinks and bobs | **take 1** | Happy blink and head bob. In take 2 the goggle eyes go dark like sunglasses. |

The intake, camera and bumper have no generated shot. They are slow zooms on the original Flop art (free, done in ffmpeg).
Square refs 01–03 were widened to 16:9 by extending their background (`refs/16x9/`) so Runway wouldn't crop Flop's wheels.

## Timeline
| Time | Picture | Caption |
|---|---|---|
| 0–5 | Shot 1 | MEET FLOP! |
| 5–9 | Flop, slow push-in | 5 PARTS |
| 9–14 | Shot 2 | WHEELS = LEGS |
| 14–19.5 | Zoom to intake | INTAKE = MOUTH |
| 19.5–25.5 | Shot 3 (+1 s hold) | ARM = NECK |
| 25.5–30.5 | Zoom to eyes | CAMERA = EYES, then RED BLUE YELLOW |
| 30.5–34.5 | Zoom to bumper | BUMPER = NOSE, then BOOP! |
| 34.5–40.5 | Shot 4 (+1 s hold) | 5 PARTS - 1 ROBOT - 1 TEAM, then LET'S BUILD IT! |
| 40.5–46.5 | "Try it!" card | Point to each part on our real robot! |

## Adding your voice
1. Record the `voiceover_script` (English, and Spanish if you like). Reading along with `draft.srt` keeps it close to the timing.
2. Put the file at e.g. `output/v1/voice_en.m4a`.
3. In `edits/v1.json` add `"voice": "output/v1/voice_en.m4a"`, set `"out": "output/v1/final.mp4"`, remove `"watermark"`,
   and nudge segment `dur` / caption `start`/`end` so they line up with your actual reading.
4. Run `python3 source/assemble.py edits/v1.json`. Re-editing is free; only new generations cost credits.
