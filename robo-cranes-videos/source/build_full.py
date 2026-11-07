"""Build the full "Robo Cranes: Level Up Lessons" video with voice, music and sound effects.

python3 source/build_full.py edits/full.json

For every part in the plan it:
  0. trims the silence around each Runway voice line (audio/voice/*.mp3 -> audio/voice_trim/*.wav);
  1. fits the part's timeline to the real voice lines (audio/voice_trim/<voice>_NN.wav). The drafts' guessed
     narration times are anchors; segments, captions and sound effects are stretched or squeezed between them;
  2. optionally adds a "LESSON n" chapter card (with a whoosh) at the start;
  3. renders the part with source/assemble.py (voice + sfx + music that ducks under the voice);
then joins all parts into one video with one narration subtitle track, normalized to -16 LUFS.
SKIP_RENDER=1 re-uses parts that are already rendered (delete a part's mp4 to re-render just that part).
Each part is also a finished stand-alone video in output/full/parts/.
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assemble  # noqa: E402

FPS = assemble.FPS
TRIM = ("silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.04,areverse,"
        "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.08,areverse,"
        "aresample=48000,aformat=channel_layouts=stereo")


def ensure_trimmed():
    """audio/voice/*.mp3 (from Runway) -> audio/voice_trim/*.wav with the silence at both ends removed."""
    os.makedirs("audio/voice_trim", exist_ok=True)
    durs = {}
    for f in sorted(os.listdir("audio/voice")):
        if not f.endswith(".mp3"):
            continue
        w = os.path.join("audio/voice_trim", f[:-4] + ".wav")
        if not os.path.exists(w):
            assemble.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join("audio/voice", f), "-af", TRIM, w])
        durs[f[:-4]] = round(duration(w), 3)
    json.dump(durs, open("audio/voice_trim/durations.json", "w"), indent=1)
    return durs


def fit(edit, voice, chapter, chapter_dur, sfx, music, out):
    e = json.loads(json.dumps(edit))
    nar = e["narration"]
    n = len(nar)
    d = [DUR[f"{voice}_{i + 1:02d}"] for i in range(n)]
    ns = [nar[0]["start"]]
    for i in range(n):
        if i + 1 < n:
            gap = max(0.35, nar[i + 1]["start"] - nar[i]["end"])
            ns.append(ns[i] + d[i] + gap)
    ne = [ns[i] + d[i] for i in range(n)]
    T_old = sum(s["dur"] for s in e["segments"])
    T_new = ne[-1] + (T_old - nar[-1]["end"])
    xs, ys = [0.0], [0.0]
    for i in range(n):
        xs += [nar[i]["start"], nar[i]["end"]]
        ys += [ns[i], ne[i]]
    xs.append(T_old); ys.append(T_new)
    assert all(a < b for a, b in zip(xs, xs[1:])), f"{voice}: narration times must increase"
    f = lambda t: float(np.interp(t, xs, ys))

    # segment boundaries -> warped, snapped to whole frames
    b_old = np.cumsum([0] + [s["dur"] for s in e["segments"]])
    b_new = [round(f(b) * FPS) / FPS for b in b_old]
    for s, a, b in zip(e["segments"], b_new, b_new[1:]):
        s["dur"] = round(b - a, 4)
    for c in e.get("captions", []):
        c["start"], c["end"] = round(f(c["start"]), 3), round(max(f(c["end"]), f(c["start"]) + 0.4), 3)
    e["narration"] = [{"start": round(ns[i], 3), "end": round(ne[i], 3), "text": nar[i]["text"]} for i in range(n)]
    e["voice_clips"] = [{"src": f"audio/voice_trim/{voice}_{i + 1:02d}.wav", "start": round(ns[i], 3)} for i in range(n)]
    e["sfx"] = [{"src": f"audio/sfx/{x[0]}.mp3", "start": round(f(x[1]), 3), "volume": x[2] if len(x) > 2 else 0.55} for x in sfx]
    e.pop("watermark", None)

    if chapter:
        title, line, bg = chapter
        e["segments"].insert(0, {"note": "chapter card", "type": "card", "dur": chapter_dur,
                                 "card": {"background": bg, "title": title, "lines": [line]}})
        for c in e.get("captions", []) + e["narration"] + e["voice_clips"] + e["sfx"]:
            for k in ("start", "end"):
                if k in c:
                    c[k] = round(c[k] + chapter_dur, 3)
        e["sfx"].insert(0, {"src": "audio/sfx/whoosh.mp3", "start": 0.0, "volume": 0.5})
    e["music"] = music
    e["out"] = out
    return e


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout)


def main(plan_path):
    global DUR
    DUR = ensure_trimmed()
    plan = json.load(open(plan_path))
    os.makedirs("edits/voiced", exist_ok=True)
    os.makedirs("output/full/parts", exist_ok=True)
    outs, srt_lines, offset = [], [], 0.0
    for p in plan["parts"]:
        name = os.path.splitext(os.path.basename(p["edit"]))[0]
        e = fit(json.load(open(p["edit"])), p["voice"], p.get("chapter"), plan.get("chapter_card_dur", 2.4),
                p.get("sfx", []), p.get("music"), f"output/full/parts/{name}.mp4")
        vp = f"edits/voiced/{name}.json"
        json.dump(e, open(vp, "w"), indent=1)
        if not os.environ.get("SKIP_RENDER") or not os.path.exists(e["out"]):
            assemble.main(vp)
        dur = duration(e["out"])
        for ln in e["narration"]:
            srt_lines.append((ln["start"] + offset, ln["end"] + offset, ln["text"]))
        offset += dur
        outs.append(e["out"])
    out = plan["out"]
    lst = os.path.splitext(out)[0] + "_parts.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(o)}'\n" for o in outs))
    srt = os.path.splitext(out)[0] + ".srt"
    with open(srt, "w") as fh:
        for i, (a, b, t) in enumerate(srt_lines, 1):
            fh.write(f"{i}\n{assemble.srt_time(a)} --> {assemble.srt_time(b)}\n{t}\n\n")
    assemble.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", srt,
                  "-map", "0:v", "-map", "0:a", "-map", "1:s", "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                  "-metadata:s:s:0", "language=eng", "-metadata", f"title={plan['title']}", "-movflags", "+faststart", out])
    os.remove(lst)
    loudnorm(out)
    print(f"wrote {out} ({offset:.1f}s, {len(outs)} parts) and {srt}")


def loudnorm(path, target=-16):
    """Two-pass loudness normalization of the audio (video and subtitles copied) to the usual web/phone level."""
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-map", "0:a", "-af",
                        f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):])
    m = (f"measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
         f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}")
    tmp = path + ".tmp.mp4"
    assemble.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-map", "0", "-c:v", "copy", "-c:s", "copy",
                  "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11:{m}:linear=true,aresample=48000",
                  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp])
    os.replace(tmp, path)


if __name__ == "__main__":
    main(sys.argv[1])
