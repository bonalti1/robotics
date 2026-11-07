"""Run Runway audio jobs (text-to-speech, sound effects / music loops), 3 at a time, and download the results.

Usage: python3 source/runway_audio.py <jobs.json> <log.json>
jobs.json: [{"out": "audio/x.mp3", "endpoint": "/text_to_speech" | "/sound_effect", "body": {...}}, ...]
Resumable: finished files are skipped and logged task ids are reused (no double spending).
In the Claude cloud session a proxy injects the Runway key; on your own computer set RUNWAYML_API_SECRET.
"""
import json, os, subprocess, sys, time

API = "https://api.dev.runwayml.com/v1"
KEY = os.environ.get("RUNWAYML_API_SECRET", "dummy")
HDR = ["-H", "X-Runway-Version: 2024-11-06", "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json"]


def call(method, path, body=None):
    cmd = ["curl", "-sS", "-X", method, API + path] + HDR
    if body is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body).encode() if body is not None else None, capture_output=True, check=True)
    return json.loads(r.stdout)


def main(jobs_file, log_file):
    jobs = json.load(open(jobs_file))
    log = json.load(open(log_file)) if os.path.exists(log_file) else {}
    save = lambda: json.dump(log, open(log_file, "w"), indent=2)
    pending = [j for j in jobs if not os.path.exists(j["out"])]
    running = {}
    while pending or running:
        while pending and len(running) < 3:
            j = pending.pop(0)
            if j["out"] in log and log[j["out"]].get("status") != "FAILED":
                tid = log[j["out"]]["task"]
            else:
                resp = call("POST", j["endpoint"], j["body"])
                if "id" not in resp:
                    print("SUBMIT ERROR", j["out"], resp, flush=True)
                    log[j["out"]] = {"status": "FAILED", "error": resp, "body": j["body"]}; save()
                    continue
                tid = resp["id"]
                log[j["out"]] = {"task": tid, "status": "SUBMITTED", "estimate": resp.get("estimatedCost"), "body": j["body"]}; save()
            running[tid] = j
        time.sleep(4)
        for tid, j in list(running.items()):
            t = call("GET", f"/tasks/{tid}")
            st = t.get("status")
            if st == "SUCCEEDED":
                os.makedirs(os.path.dirname(j["out"]) or ".", exist_ok=True)
                subprocess.run(["curl", "-sS", "-L", "-o", j["out"], t["output"][0]], check=True)
                log[j["out"]]["status"] = "SUCCEEDED"; save()
                print("done", j["out"], flush=True); del running[tid]
            elif st in ("FAILED", "CANCELLED"):
                log[j["out"]]["status"] = "FAILED"; log[j["out"]]["error"] = t.get("failure"); save()
                print("FAILED", j["out"], t.get("failure"), flush=True); del running[tid]
    print("all finished", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
