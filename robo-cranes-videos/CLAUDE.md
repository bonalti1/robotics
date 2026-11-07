# Robo Cranes teaching videos (VEX IQ Level Up, 3rd grade)

## What this project is
Short teaching videos (30–60 s) for the Robo Cranes, a 3rd–5th grade VEX IQ robotics team at Grulla Elementary
(season: Level Up 2026–27, competition Dec 10). The team's coach is a teacher at the school; Rolando is a parent
volunteer who works with the coach and makes the teaching materials (videos, challenge cards, voiceover). Audience: 8–10 year olds.
Mascot: **Cranebot**, an original cartoon robot crane (refs/01_mascot_hero.png). Robot: **Flop**, drawn as an original cartoon (refs/02, 03).

## The job
`videos.json` lists 6 videos. For each video:
1. For each shot: image-to-video from `reference_image` + `motion_prompt`, 5 seconds, 16:9.
   Use Runway or Higgsfield (whichever is set up). Make 2 takes per shot, keep the better one.
   Save to `output/<video id>/shot<n>_take<k>.mp4`.
2. Voiceover: Rolando prefers to record it himself (real voice, maybe a Spanish version too).
   If he asks for AI voice: warm, friendly, slow, kid-oriented, from `voiceover_script`.
3. Assemble with ffmpeg: shots in order, trim/hold to match the voice length, add the voice,
   add BIG captions for key words (e.g. "1 point", "3 points", "6 points!") during editing, not inside generated frames.
   Output `output/<video id>/final.mp4` (1920x1080) and a 1080x1920 vertical cut if asked.

## Pipeline (built while making v1; reuse for v2–v6)
- **Generator:** Runway Gen-4.5 (`gen4.5`, 12 credits/s → 60 credits per 5 s take). Rolando asked for the best model.
  v1 cost 480 credits (4 shots × 2 takes). Higgsfield had only ~24 credits, so it isn't used.
- `source/pad16x9.py <in> <out> <left share>` widens square refs to 16:9 by extending the background (`refs/16x9/`),
  so Runway doesn't crop the art. 1920x1080 refs (04–07, 09) are used as they are.
- `source/runway_gen.py output/<id>/jobs.json output/<id>/runway_log.json` submits the takes (3 at a time), downloads
  them, and logs seeds and task ids. It can be resumed and skips finished files.
- `source/assemble.py edits/<id>.json` builds the video from a timeline: generated clips, free ffmpeg zooms on the
  ref art, BIG captions, a "Try it!" hands-on challenge card at the end, and a narration `.srt`. See `output/v1/NOTES.md`.
- Each video ends with a short **"Try it!"** card: a hands-on challenge that links the video's idea to the real robot
  (watch → try → measure → decide), so the kids learn while getting better at the game.

## Rules (do not break)
- **Ask Rolando before spending credits.** Quote the estimated cost per video first; start with ONE video (v1) as a test.
- No text inside generated frames (generators garble it). All words go in as captions in the edit.
- Keep the flat 2D cartoon style of the references; one simple motion per shot; static camera unless the prompt says pan/zoom.
- Only use the original images in `refs/`. Do NOT feed VEX Robotics' photos/videos or news photos into generators (copyrighted).
  Link to VEX's videos instead (see source/video_kit.html, "Watch & learn").
- Game facts must stay exact: floor goal = 1 pt, pyramid L1 = 3 pts, a bag stacked on L1 reaching L2 = 6 pts; bags must match
  the goal color, yellow counts on any goal; a bag touching the robot scores 0; the arm must be DOWN to pass under the barrier.
  Higher tiers (L3/L4) are intentionally left out for 3rd graders.
- VEX is student-centered: these videos teach concepts. Never make content that gives kids a finished competition program to copy.
- No real children's faces in generated content.

## Already built (for context)
- Flop Academy (interactive games): https://claude.ai/artifact/SLNoVEN74XzRi7BftyLZge  (source/flop_academy.html)
- Video Kit page: https://claude.ai/artifact/DksT21Mb1fnn4ZmFehs733 (source/video_kit.html)
- Session 1 deck: https://claude.ai/artifact/PHuAeJ2hmcox65SUkLaFb7
- Coach playbook: https://claude.ai/artifact/X8fCqsvKRNZbFG8DC53k6G
- `source/reference_art.py` + `source/mascot.py` regenerate the reference images (SVG → PNG) if a new pose is needed.
