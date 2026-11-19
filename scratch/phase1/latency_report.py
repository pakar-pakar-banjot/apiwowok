"""P1-10: summarize the NRT latency poller output (data/firms/latency/{polls,observations}.csv).
Latency = first poll that returned the detection - (acq_date + acq_time, UTC). Only detections first seen AFTER the
baseline poll count (the baseline returns everything already published). Resolution = poll interval.
Writes data/firms/profile/latency.json."""
import pathlib, csv, json, collections, datetime as dt
import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[2]
LAT = REPO / "data" / "firms" / "latency"; PROF = REPO / "data" / "firms" / "profile"
polls = list(csv.DictReader(open(LAT / "polls.csv", encoding="utf-8")))
obs = list(csv.DictReader(open(LAT / "observations.csv", encoding="utf-8")))
base = {}
for p in polls:
    base.setdefault(p["source"], p["poll_utc"])


def acq(o):
    t = o["acq_time"].zfill(4)
    return dt.datetime.fromisoformat(f"{o['acq_date']}T{t[:2]}:{t[2:]}:00+00:00")


lat = collections.defaultdict(list); batches = collections.defaultdict(collections.Counter)
events = collections.Counter()
for o in obs:
    after = o["first_seen_utc"] > base[o["source"]]
    events[f"{o['event']}|{o['source']}|{'after_baseline' if after else 'baseline'}"] += 1
    if o["event"] == "new" and after:
        m = (dt.datetime.fromisoformat(o["first_seen_utc"]) - acq(o)).total_seconds() / 60
        lat[o["source"]].append(m)
        batches[o["source"]][(o["first_seen_utc"][:16], o["daynight"])] += 1
q = lambda a: {"n": len(a), "min": round(min(a)), "p50": round(float(np.percentile(a, 50))),
               "p90": round(float(np.percentile(a, 90))), "max": round(max(a))} if a else {}
out = {
    "polls": len(polls), "first_poll_utc": polls[0]["poll_utc"] if polls else None,
    "last_poll_utc": polls[-1]["poll_utc"] if polls else None,
    "poll_http": dict(collections.Counter(p["http"] for p in polls)),
    "events": dict(events),
    "latency_minutes_new_after_baseline": {s: q(v) for s, v in lat.items()},
    "arrival_batches": {s: [f"{k[0]}Z {k[1]}: {n}" for k, n in sorted(c.items())] for s, c in batches.items()},
}
(PROF / "latency.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
