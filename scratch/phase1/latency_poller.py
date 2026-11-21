"""P1-10: poll FIRMS NRT (bbox Indonesia) every N minutes; log first-seen time per detection and changes.
Output: data/firms/latency/observations.csv (one row per new or changed detection). Never prints MAP_KEY."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import csv, io, time, datetime as dt, requests
from firms_common import BASE, BBOX, DATA, map_key, redact
SOURCES = ["VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]
INTERVAL_MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 15
HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 24
RESUME = len(sys.argv) > 3 and sys.argv[3] == "resume"  # continue an earlier run: keys already logged are not "new"
k = map_key(); out = DATA / "latency"; out.mkdir(parents=True, exist_ok=True)
obs = out / "observations.csv"; polls = out / "polls.csv"
seen = {}  # key -> row signature
for p, hdr in ((obs, ["first_seen_utc","event","source","latitude","longitude","acq_date","acq_time","confidence","frp","version","daynight","prev_signature"]),
               (polls, ["poll_utc","source","http","rows","new","changed","disappeared"])):
    if not p.exists(): p.write_text(",".join(hdr) + "\n", encoding="utf-8")
if RESUME:  # signature of earlier rows is unknown -> None; the first poll re-learns it silently (no "changed" event)
    for o in csv.DictReader(open(obs, encoding="utf-8")):
        seen.setdefault((o["source"], o["latitude"], o["longitude"], o["acq_date"], o["acq_time"]), None)
    print("resumed with", len(seen), "known detections", flush=True)
if sys.platform == "win32":  # keep Windows from idle-sleeping while this process runs (auto-reverts on exit)
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
end = time.time() + HOURS * 3600
while time.time() < end:
    for src in SOURCES:
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        try:
            r = requests.get(f"{BASE}/api/area/csv/{k}/{src}/{BBOX}/2", timeout=180)
        except requests.RequestException as e:
            print(now, src, "error", redact(str(e), k)[:150], flush=True); continue
        if r.status_code != 200 or not r.text.startswith("latitude"):
            print(now, src, "bad", r.status_code, redact(r.text, k)[:150], flush=True)
            with open(polls, "a", encoding="utf-8") as f: f.write(f"{now},{src},{r.status_code},,,,\n")
            continue
        rows = list(csv.DictReader(io.StringIO(r.text)))
        cur = set(); new = chg = 0
        with open(obs, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for x in rows:
                key = (src, x["latitude"], x["longitude"], x["acq_date"], x["acq_time"]); cur.add(key)
                sig = "|".join(x.get(c, "") for c in ("bright_ti4","bright_ti5","frp","confidence","scan","track","version","daynight"))
                if key not in seen:
                    new += 1; w.writerow([now, "new", src, *key[1:], x["confidence"], x["frp"], x["version"], x["daynight"], ""])
                elif seen[key] is not None and seen[key] != sig:
                    chg += 1; w.writerow([now, "changed", src, *key[1:], x["confidence"], x["frp"], x["version"], x["daynight"], seen[key]])
                seen[key] = sig
        gone = sum(1 for kk in seen if kk[0] == src and kk not in cur)
        with open(polls, "a", encoding="utf-8") as f: f.write(f"{now},{src},200,{len(rows)},{new},{chg},{gone}\n")
        print(now, src, "rows", len(rows), "new", new, "changed", chg, "not_in_window", gone, flush=True)
    time.sleep(INTERVAL_MIN * 60)
print("POLLER DONE")
