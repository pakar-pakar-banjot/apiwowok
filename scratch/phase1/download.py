"""Phase 1 one-off FIRMS Area API downloader (bbox Indonesia + margin). Never prints MAP_KEY."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import csv, hashlib, time, datetime as dt, requests
from firms_common import BASE, BBOX, DATA, map_key, redact

PLAN = [  # (source, first_date, last_date) inclusive, within data_availability (2026-11-19)
    ("VIIRS_NOAA20_SP",  "2023-01-01", "2026-07-31"),
    ("VIIRS_NOAA21_SP",  "2023-03-01", "2026-07-31"),
    ("VIIRS_NOAA20_NRT", "2026-08-01", "2026-11-18"),
    ("VIIRS_NOAA21_NRT", "2025-08-01", "2026-11-18"),
]
LIMIT_SOFT = 4000
k = map_key()
manifest = DATA / "manifest.csv"
new = not manifest.exists()
mf = open(manifest, "a", newline="", encoding="utf-8"); mw = csv.writer(mf)
if new: mw.writerow(["source","start","days","http","rows","bytes","sha256","fetched_at_utc","file"])

def tx():
    r = requests.get(f"{BASE}/mapserver/mapkey_status/", params={"MAP_KEY": k}, timeout=60)
    return r.json()["current_transactions"]

for src, a, b in PLAN:
    d, end = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    out = DATA / "raw" / src; out.mkdir(parents=True, exist_ok=True)
    while d <= end:
        days = min(5, (end - d).days + 1)
        f = out / f"{d.isoformat()}_{days}d.csv"
        if not f.exists():
            while tx() > LIMIT_SOFT:
                print("quota pause", flush=True); time.sleep(60)
            for attempt in range(4):
                try:
                    r = requests.get(f"{BASE}/api/area/csv/{k}/{src}/{BBOX}/{days}/{d.isoformat()}", timeout=180)
                    if r.status_code == 200 and r.text.startswith("latitude"): break
                    print("bad response", src, d, r.status_code, redact(r.text, k)[:200], flush=True)
                except requests.RequestException as e:
                    print("error", src, d, redact(str(e), k)[:200], flush=True)
                time.sleep(20 * (attempt + 1))
            else:
                raise SystemExit(f"giving up at {src} {d}")
            f.write_bytes(r.content)
            mw.writerow([src, d.isoformat(), days, r.status_code, r.text.count("\n") - 1 + (not r.text.endswith("\n")),
                         len(r.content), hashlib.sha256(r.content).hexdigest(),
                         dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), f.relative_to(DATA).as_posix()])
            mf.flush()
        d += dt.timedelta(days=days)
    print("done", src, flush=True)
print("ALL DONE")
