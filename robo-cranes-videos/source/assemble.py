"""Assemble a Robo Cranes teaching video from an edit timeline (edits/<id>.json) with ffmpeg.

Usage (from the project folder):  python3 source/assemble.py edits/v1.json

Timeline JSON:
  segments  - played in order. {"type": "clip", "src": mp4, "dur": s, "src_end": s}  (shorter clips hold their
              last frame; optional "src_end" uses only the first seconds of the clip)
              or {"type": "still", "src": png, "dur": s, "zoom": {"to": 1.8, "cx": px, "cy": px}}  (slow push-in
              toward point cx,cy given in 1920x1080 pixels, optional "ease": 0.7 share of the shot spent zooming;
              omit "zoom" for a plain hold; optional "wobble": {"deg": 4, "period": 3} gently rocks the picture)
  captions  - BIG key-word captions burned in during editing (never inside generated frames).
              {"start": s, "end": s, "parts": [["WHEELS", "white"], [" = ", "yellow"], ["LEGS", "cyan"]],
               "pos": "top"|"bottom"|"topleft"|"topright"|[x, y], "size": 118}
              {"type": "card", "dur": s, "card": {"background": png, "title": "TRY IT!", "lines": [...], "footer": "..."}}
              is also a segment type: a full-frame end card (e.g. the hands-on challenge).
  narration - voiceover lines with timings; written to <out>.srt and embedded as a toggleable subtitle track,
              so the voice can be recorded to the same timing (or the timing changed to fit the voice).
  voice     - optional path to one recorded voiceover file (wav/m4a/mp3) starting at 0 s.
  voice_clips - optional [{"src": wav, "start": s}] voice lines placed on the timeline (see source/voiced.py).
  sfx       - optional [{"src": mp3, "start": s, "volume": 0.55}] sound effects.
  music     - optional {"src": mp3, "volume": 0.3}: looped under everything, ducking whenever voice/sfx play.
              Without voice, sfx and music the video gets a silent track.
  watermark - optional small corner label, e.g. "DRAFT - no voice yet".
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_SMALL = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
COLORS = {"navy": "#1c2340", "cream": "#fff8ec", "white": "#ffffff", "yellow": "#f5c400", "red": "#e5484d",
          "blue": "#3e7bfa", "green": "#22a06b", "purple": "#8a63d2", "cyan": "#5ef0ff"}


def col(c):
    return COLORS.get(c, c)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-3000:]}")


def caption_png(parts, pos, path, size=118):
    """Rounded navy pill with thick outline and multi-colour bold text, on a transparent 1920x1080 canvas."""
    font = ImageFont.truetype(FONT, size)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    widths = [d.textlength(t, font=font) for t, _ in parts]
    tw = sum(widths)
    asc, desc = font.getmetrics()
    th = asc + desc
    padx, pady = 64, 30
    bw, bh = tw + 2 * padx, th + 2 * pady
    if isinstance(pos, list):  # explicit [x, y] of the pill's top-left corner
        x0, y0 = pos
    else:
        x0 = {"topleft": 56, "topright": W - bw - 56}.get(pos, (W - bw) / 2)
        y0 = H - bh - 40 if pos == "bottom" else 44
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=bh / 2, fill=col("navy"), outline=col("white"), width=8)
    x = x0 + padx
    for (t, c), w in zip(parts, widths):
        d.text((x, y0 + pady), t, font=font, fill=col(c))
        x += w
    img.save(path)


def draw_block(d, b, y):
    """A simple drawn code block (illustration of a VEXcode-style block, not a screenshot).
    b = {"text": "turn to heading 90 degrees", "extra": "and don't wait", "mark": "check"|"x", "dim": false}"""
    f = ImageFont.truetype(FONT_SMALL, b.get("size", 64))
    h, pad = round(b.get("size", 64) * 1.9), 44
    tw = d.textlength(b["text"], font=f)
    ew = d.textlength(b["extra"], font=f) + 2 * pad if b.get("extra") else 0
    arrow = 70
    bw = tw + 2 * pad + arrow + ew
    x0 = (W - bw) / 2
    fill = "#9fb7e8" if b.get("dim") else col("blue")
    d.rounded_rectangle([x0, y, x0 + bw, y + h], radius=26, fill=fill, outline=col("navy"), width=6)
    d.text((x0 + pad, y + h / 2), b["text"], font=f, fill="white", anchor="lm")
    ax = x0 + pad + tw + 24  # the little expand arrow
    d.polygon([(ax, y + h / 2 - 20), (ax, y + h / 2 + 20), (ax + 30, y + h / 2)], fill="white")
    if b.get("extra"):
        ex = ax + arrow - 14
        d.rounded_rectangle([ex, y + 14, ex + ew, y + h - 14], radius=20, fill=col("yellow"), outline=col("navy"), width=5)
        d.text((ex + ew / 2, y + h / 2), b["extra"], font=f, fill=col("navy"), anchor="mm")
    m, mx, my = b.get("mark"), x0 - 90, y + h / 2
    if m == "check":
        d.line([(mx - 34, my), (mx - 8, my + 28), (mx + 38, my - 30)], fill=col("green"), width=18, joint="curve")
    elif m == "x":
        d.line([(mx - 30, my - 30), (mx + 30, my + 30)], fill=col("red"), width=18)
        d.line([(mx - 30, my + 30), (mx + 30, my - 30)], fill=col("red"), width=18)
    return y + h


def card_png(card, path):
    """Full-frame end card (e.g. the "Try it!" challenge) over a dimmed background image."""
    bg = Image.open(card["background"]).convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
    img = Image.blend(bg, Image.new("RGB", (W, H), col("cream")), 0.82).convert("RGBA")
    d = ImageDraw.Draw(img)
    title = ImageFont.truetype(FONT, 150)
    body = ImageFont.truetype(FONT, 82)
    small = ImageFont.truetype(FONT_SMALL, 56)
    t = card["title"]
    tw = d.textlength(t, font=title)
    bw, bh = tw + 140, 210
    x0, y0 = (W - bw) / 2, 200
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=bh / 2, fill=col("yellow"), outline=col("navy"), width=10)
    d.text((W / 2, y0 + bh / 2), t, font=title, fill=col("navy"), anchor="mm")
    y = 520
    for b in card.get("blocks", []):
        y = draw_block(d, b, y) + 50
    if card.get("blocks"):
        y += 30
    for line in card.get("lines", []):
        d.text((W / 2, y), line, font=body, fill=col("navy"), anchor="mm")
        y += 110
    if card.get("footer"):
        d.text((W / 2, y + 40), card["footer"], font=small, fill=col("purple"), anchor="mm")
    img.convert("RGB").save(path)


def watermark_png(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SMALL, 24)
    d.text((W - 24, H - 10), text, font=f, fill=(28, 35, 64, 140), anchor="rs")
    img.save(path)


def render_segment(seg, out, tmp):
    dur = seg["dur"]
    n = round(dur * FPS)
    norm = f"scale={W}:{H}:flags=lanczos,fps={FPS},format=yuv420p"
    if seg["type"] == "clip":
        cut = f"trim=end={seg['src_end']},setpts=PTS-STARTPTS," if seg.get("src_end") else ""  # use only the start of the clip
        vf = f"{cut}{norm},tpad=stop_mode=clone:stop_duration={dur},trim=duration={dur},setpts=PTS-STARTPTS"
        run(["ffmpeg", "-y", "-v", "error", "-i", seg["src"], "-an", "-vf", vf, "-frames:v", str(n),
             "-c:v", "libx264", "-crf", "16", "-preset", "medium", out])
        return
    src = seg.get("src")
    if seg["type"] == "card":
        src = os.path.join(tmp, os.path.basename(out) + ".png")
        card_png(seg["card"], src)
    z = seg.get("zoom")
    if z:
        # Ease (smoothstep) from the full frame toward (cx, cy) over the first 70% of the shot, then hold.
        # Work on a 2x upscale so zoompan's integer positioning doesn't jitter.
        k = max(1, round(n * z.get("ease", 0.7)))  # "ease": share of the shot spent moving
        s = f"(3*pow(min(on/{k},1),2)-2*pow(min(on/{k},1),3))"
        zt, cx, cy = z["to"], z["cx"] * 2, z["cy"] * 2
        zexp = f"1+{zt - 1}*{s}"
        xexp = f"max(0,min(iw-iw/zoom,({W}+({cx}-{W})*{s})-iw/zoom/2))"
        yexp = f"max(0,min(ih-ih/zoom,({H}+({cy}-{H})*{s})-ih/zoom/2))"
        vf = (f"scale={2 * W}:{2 * H}:flags=lanczos,zoompan=z='{zexp}':x='{xexp}':y='{yexp}':d=1:s={W}x{H}:fps={FPS},"
              f"format=yuv420p")
    else:
        vf = norm
    if seg.get("wobble"):  # gentle rocking, e.g. {"deg": 4, "period": 3}: a = -deg*sin(2*pi*t/period)
        wb = seg["wobble"]
        vf += f",rotate=a='-{wb['deg']}*PI/180*sin(2*PI*t/{wb['period']})':c=0xfff8ec"
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", src, "-vf", vf,
         "-frames:v", str(n), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-tune", "stillimage", out])


def build_audio(e, total, tmp):
    """Mix voice clips + sound effects, with optional looping music that ducks under them. Returns a wav path."""
    out = os.path.join(tmp, "mix.wav")
    clips = list(e.get("voice_clips", []))
    if e.get("voice"):
        clips.append({"src": e["voice"], "start": 0})
    fx = [dict(c, volume=c.get("volume", 1.0)) for c in clips] + [dict(c, volume=c.get("volume", 0.55)) for c in e.get("sfx", [])]
    music = e.get("music")
    if not fx and not music:
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", out])
        return out
    cmd, chain = ["ffmpeg", "-y", "-v", "error"], []
    norm = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    for k, c in enumerate(fx):
        cmd += ["-i", c["src"]]
        ms = max(0, round(c["start"] * 1000))
        chain.append(f"[{k}:a]{norm},volume={c['volume']},adelay={ms}:all=1[c{k}]")
    if fx:
        chain.append("".join(f"[c{k}]" for k in range(len(fx))) +
                     f"amix=inputs={len(fx)}:normalize=0:duration=longest,apad,atrim=0:{total}[fg]")
    else:
        chain.append(f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=0:{total}[fg]")
    if music:
        m = len(fx)
        cmd += ["-stream_loop", "-1", "-i", music["src"]]
        fo = max(0.0, total - 1.5)
        chain.append(f"[{m}:a]{norm},atrim=0:{total},asetpts=N/SR/TB,volume={music.get('volume', 0.3)},"
                     f"afade=t=in:d=0.6,afade=t=out:st={fo:.3f}:d=1.5[mus]")
        chain.append("[fg]asplit=2[fg1][fg2]")
        chain.append("[mus][fg1]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=450[duck]")
        chain.append("[fg2][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[out]")
    else:
        chain.append("[fg]alimiter=limit=0.95[out]")
    cmd += ["-filter_complex", ";".join(chain), "-map", "[out]", "-t", f"{total}", "-c:a", "pcm_s16le", out]
    run(cmd)
    return out


def srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(edit_path):
    e = json.load(open(edit_path))
    out = e["out"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    total = sum(s["dur"] for s in e["segments"])
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, seg in enumerate(e["segments"]):
            p = os.path.join(tmp, f"seg{i:02d}.mp4")
            render_segment(seg, p, tmp)
            parts.append(p)
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        base = os.path.join(tmp, "base.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

        srt = os.path.splitext(out)[0] + ".srt"
        with open(srt, "w") as f:
            for i, ln in enumerate(e.get("narration", []), 1):
                f.write(f"{i}\n{srt_time(ln['start'])} --> {srt_time(ln['end'])}\n{ln['text']}\n\n")

        cmd = ["ffmpeg", "-y", "-v", "error", "-i", base]
        chain, last, idx = [], "0:v", 1
        overlays = [(c, None) for c in e.get("captions", [])]
        if e.get("watermark"):
            overlays.append(({"start": 0, "end": total, "watermark": e["watermark"]}, None))
        for j, (c, _) in enumerate(overlays):
            png = os.path.join(tmp, f"cap{j:02d}.png")
            if "watermark" in c:
                watermark_png(c["watermark"], png)
                fade = ""
            else:
                caption_png(c["parts"], c.get("pos", "top"), png, c.get("size", 118))
                d = c["end"] - c["start"]
                fade = f",fade=t=in:st=0:d=0.18:alpha=1,fade=t=out:st={d - 0.18:.3f}:d=0.18:alpha=1"
            d = c["end"] - c["start"]
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", png]
            chain.append(f"[{idx}:v]format=rgba{fade},setpts=PTS-STARTPTS+{c['start']}/TB[o{j}]")
            chain.append(f"[{last}][o{j}]overlay=0:0:eof_action=pass[v{j}]")
            last, idx = f"v{j}", idx + 1
        cmd += ["-i", build_audio(e, total, tmp)]
        audio_idx = idx
        cmd += ["-i", srt]
        chain_str = ";".join(chain) if chain else "[0:v]null[vout]"
        vmap = f"[{last}]" if chain else "[vout]"
        cmd += ["-filter_complex", chain_str, "-map", vmap, "-map", f"{audio_idx}:a", "-map", f"{audio_idx + 1}:s",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
                "-c:a", "aac", "-b:a", "160k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                "-t", f"{total}", "-movflags", "+faststart", out]
        run(cmd)
    print(f"wrote {out} ({total:.1f}s) and {srt}")


if __name__ == "__main__":
    main(sys.argv[1])
