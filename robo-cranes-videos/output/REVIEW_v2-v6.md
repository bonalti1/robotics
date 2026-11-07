# v2–v6 drafts — review notes

All drafts are 1920x1080, **no voice yet**, with placeholder captions and a narration subtitle track (`draft.srt`,
also embedded). The timing is a guess at a slow, kid-friendly pace; it gets re-fit to your recording.

**Generation:** Runway Gen-4.5, 24 takes (12 shots × 2), **1,440 credits ($14.40)**, exactly as quoted.
Balance went from 3,768 to **2,328**. v1 + v2–v6 used 1,920 credits ($19.20) in total.

| Video | Length | Takes kept (why) |
|---|---|---|
| **v2 How Points Work** | 43.5 s | Shot 1 take 1 (bags bounce in order; take 2 squished the red bag) · Shot 2 take 1 (steady move to the pyramids; take 2 had a bag stack fly off) · Shot 3 take 2 (clean drop; take 1 wobbled a lot) |
| **v3 The Color Rule** | 31.7 s | Shot 1 take 1 (sparkle zoom on yellow; take 2 bent the bag) · Shot 2 take 2 (field stays put while zooming to the red goal; take 1 suddenly filled both goals with color). Only its first 3 s are used, because it zooms in too tight. |
| **v4 Wait vs. Don't Wait** | 37.6 s | Shot 1 take 2 (drive, then a clear stop; take 1 rolled back) · Shot 2 take 2 (drives while the arm rises; take 1's arm snapped up at once) · Shot 3 take 1 (nod and hop; take 2's head drooped oddly) |
| **v5 Turn to Heading** | 32.6 s | Shot 2 take 1 (points at the field and nods; take 2 looked away). **Shot 1: neither take used.** Both spun the field ~90° and warped the bags, so the draft gently rocks the original field art ~4° in ffmpeg instead (free). It can be re-generated with a stricter prompt for 120 credits if you want. |
| **v6 Let's Go!** | 24.6 s | Shot 1 take 2 (wings spread wide, big smile, confetti) · Shot 2 take 1 (both bounce happily; Flop's wheels pop up on springy legs mid-bounce. Take 2 gave Flop angry eyes) |

## Things added in the edit (free, no credits)
- **Slow zooms on the original art** for beats with no generated shot (e.g. 1 / 3 / 6 points on each goal in v2,
  the blue goal and the "wrong color" red bag in v3).
- **v2:** the numbers **1, 3, 6** pop up above each goal, each one higher than the last ("higher = more points").
- **v4:** a drawn illustration of one block, `spin Arm up for 90 degrees ▸ and don't wait`.
  **v5:** `turn right for 90 degrees` ✗ vs `turn to heading 90 degrees` ✓. These are simple drawings,
  not VEXcode screenshots. The teacher can show the real thing in VEXcode.
- **v5:** two new diagrams in the same flat style (`refs/diagrams/`): the planned square vs the real path where
  small turn errors add up, and a compass with Flop facing 90° toward a window.
- **"Try it!" card** at the end of each video, a hands-on test on the real robot:
  - v2: Drop 5 bags in the same spot. How many stack up?
  - v3: Sort the bags: red to red, blue to blue. Where can yellow go?
  - v4: Time Flop both ways, wait vs. don't wait. Which is faster? Write it in your notebook!
  - v5: Drive a square: 4 turns. Where does Flop end up? Try "turn for" first, then "turn to heading".
  - v6: Pick a job to try first: Builder, Coder, Driver.

## Game facts checked against CLAUDE.md
Floor goal = 1, pyramid = 3, a bag on a bag reaching the next level = 6 ("that's double"). The bag must match the goal
color, yellow counts on any goal, and a wrong color or a bag still touching the robot = 0. No L3/L4 points are mentioned.
No finished programs, only single example blocks.

## To finish a video
Record the voiceover, put it in `output/<id>/`, add `"voice": "..."` to `edits/<id>.json`, set `"out"` to
`output/<id>/final.mp4`, remove `"watermark"`, re-fit the timings, then run `python3 source/assemble.py edits/<id>.json`.
