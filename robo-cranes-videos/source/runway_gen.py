"""Usage: python3 source/runway_gen.py output/<id>/jobs.json output/<id>/runway_log.json
Submit Runway gen4.5 image-to-video jobs (max 3 concurrent), poll, download. Resumable: skips finished files and reuses logged task ids."""
import base64, json, os, subprocess, sys, time
API = "https://api.dev.runwayml.com/v1"
# In the Claude cloud session a proxy injects the Runway key; on your own computer set RUNWAYML_API_SECRET.
KEY = os.environ.get("RUNWAYML_API_SECRET", "dummy")
HDR = ["-H", "X-Runway-Version: 2024-11-06", "-H", f"Authorization: Bearer {KEY}", "-H", "Content-Type: application/json"]

def call(method, path, body=None):
    cmd = ["curl", "-sS", "-X", method, API + path] + HDR
    if body is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body).encode() if body is not None else None, capture_output=True, check=True)
    return json.loads(r.stdout)

jobs_file, log_file = sys.argv[1], sys.argv[2]
jobs = json.load(open(jobs_file))
log = json.load(open(log_file)) if os.path.exists(log_file) else {}
def save(): json.dump(log, open(log_file, "w"), indent=2)

pending = [j for j in jobs if not os.path.exists(j["out"])]
running = {}
while pending or running:
    while pending and len(running) < 3:
        j = pending.pop(0)
        if j["out"] in log and log[j["out"]].get("status") not in ("FAILED",):
            tid = log[j["out"]]["task"]
        else:
            uri = "data:image/png;base64," + base64.b64encode(open(j["image"], "rb").read()).decode()
            body = {"model": "gen4.5", "promptImage": uri, "promptText": j["prompt"], "ratio": "1280:720", "duration": 5, "seed": j["seed"]}
            resp = call("POST", "/image_to_video", body)
            if "id" not in resp:
                print("SUBMIT ERROR", j["out"], resp, flush=True); sys.exit(1)
            tid = resp["id"]
            log[j["out"]] = {"task": tid, "seed": j["seed"], "image": j["image"], "prompt": j["prompt"], "status": "SUBMITTED"}; save()
        print("running", j["out"], tid, flush=True)
        running[tid] = j
    time.sleep(10)
    for tid, j in list(running.items()):
        t = call("GET", f"/tasks/{tid}")
        st = t.get("status")
        if st == "SUCCEEDED":
            os.makedirs(os.path.dirname(j["out"]), exist_ok=True)
            subprocess.run(["curl", "-sS", "-L", "-o", j["out"], t["output"][0]], check=True)
            log[j["out"]]["status"] = "SUCCEEDED"; save()
            print("done", j["out"], flush=True); del running[tid]
        elif st in ("FAILED", "CANCELLED"):
            log[j["out"]]["status"] = "FAILED"; log[j["out"]]["error"] = t.get("failure") or t; save()
            print("FAILED", j["out"], t.get("failure"), t.get("failureCode"), flush=True); del running[tid]
print("all finished", flush=True)
