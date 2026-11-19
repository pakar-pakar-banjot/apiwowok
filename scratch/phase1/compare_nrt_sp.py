"""P1-11: compare NOAA-21 NRT vs SP on overlapping dates (row level).
Match rule: same acq_date, |acq_time diff| <= TMAX minutes, nearest location within RMAX km.
Writes data/firms/profile/nrt_vs_sp.json. Indonesia-only via coord_assign.csv."""
import pathlib, csv, json, math, collections, datetime as dt
import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "firms" / "raw"; OUT = REPO / "data" / "firms" / "profile"
A, B = "VIIRS_NOAA21_NRT", "VIIRS_NOAA21_SP"
D0, D1 = dt.date(2025, 8, 1), dt.date(2026, 7, 31)
TMAX, RMAX = 2, 1.0
assign = {}
with open(OUT / "coord_assign.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        assign[(r["latitude"], r["longitude"])] = r["kdppum"]


def load(src):
    out = collections.defaultdict(list)
    for f in sorted((RAW / src).glob("*.csv")):
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                d = dt.date.fromisoformat(r["acq_date"])
                if D0 <= d <= D1 and assign.get((r["latitude"], r["longitude"])):
                    out[r["acq_date"]].append(r)
    return out


def tmin(t):
    t = int(t); return (t // 100) * 60 + t % 100


def km(a, b):
    la1, lo1, la2, lo2 = map(float, (a["latitude"], a["longitude"], b["latitude"], b["longitude"]))
    return math.hypot((lo2 - lo1) * 111.32 * math.cos(math.radians((la1 + la2) / 2)), (la2 - la1) * 110.57)


def dec(s):
    return len(s.split(".")[1]) if "." in s else 0


nrt, sp = load(A), load(B)
res = collections.Counter(); dists = []; dfrp = []; dti4 = []; dtime = collections.Counter()
conf = collections.Counter(); dn = collections.Counter(); per_day = []
decs = {"NRT": collections.Counter(), "SP": collections.Counter()}
cols = {}
for day in sorted(set(nrt) | set(sp)):
    N, S = nrt.get(day, []), sp.get(day, [])
    per_day.append((day, len(N), len(S)))
    for r in N[:50]: decs["NRT"][dec(r["latitude"])] += 1
    for r in S[:50]: decs["SP"][dec(r["latitude"])] += 1
    if N: cols["NRT"] = list(N[0].keys())
    if S: cols["SP"] = list(S[0].keys())
    grid = collections.defaultdict(list)
    for j, s in enumerate(S):
        grid[(int(float(s["latitude"]) * 50), int(float(s["longitude"]) * 50))].append(j)
    exact = {(s["latitude"], s["longitude"], s["acq_time"]) for s in S}
    used = set()
    for r in N:
        if (r["latitude"], r["longitude"], r["acq_time"]) in exact:
            res["exact_key_match"] += 1
        gy, gx = int(float(r["latitude"]) * 50), int(float(r["longitude"]) * 50)
        best = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for j in grid.get((gy + dy, gx + dx), ()):
                    s = S[j]
                    if abs(tmin(s["acq_time"]) - tmin(r["acq_time"])) > TMAX:
                        continue
                    dd = km(r, s)
                    if dd <= RMAX and (best is None or dd < best[0]):
                        best = (dd, j)
        if best is None:
            res["nrt_unmatched"] += 1; continue
        res["nrt_matched"] += 1; dd, j = best; s = S[j]
        if j in used: res["sp_matched_more_than_once"] += 1
        used.add(j); dists.append(dd * 1000)
        dfrp.append(float(r["frp"]) - float(s["frp"])); dti4.append(float(r["bright_ti4"]) - float(s["bright_ti4"]))
        dtime[tmin(r["acq_time"]) - tmin(s["acq_time"])] += 1
        conf[(r["confidence"], s["confidence"])] += 1; dn[(r["daynight"], s["daynight"])] += 1
    res["sp_unmatched"] += len(S) - len(used)
    res["nrt_rows"] += len(N); res["sp_rows"] += len(S)
pd_arr = np.array([(n, s) for _, n, s in per_day], dtype=float)
ratio = np.divide(pd_arr[:, 0], pd_arr[:, 1], out=np.full(len(pd_arr), np.nan), where=pd_arr[:, 1] > 0)
q = lambda a, qs: {f"p{x}": round(float(np.percentile(a, x)), 3) for x in qs} if len(a) else {}
out = {
    "window": [str(D0), str(D1)], "match_rule": f"same acq_date, |dt|<={TMAX} min, nearest <= {RMAX} km", "counts": dict(res),
    "columns": cols, "lat_decimals_sample": {k: dict(v) for k, v in decs.items()},
    "distance_m_matched": q(np.array(dists), [50, 90, 99, 100]),
    "share_distance_0m": round(float(np.mean(np.array(dists) == 0)), 4) if dists else None,
    "frp_diff_nrt_minus_sp": q(np.array(dfrp), [1, 50, 99]), "share_frp_equal": round(float(np.mean(np.array(dfrp) == 0)), 4) if dfrp else None,
    "ti4_diff_nrt_minus_sp": q(np.array(dti4), [1, 50, 99]),
    "acq_time_diff_min": dict(sorted(dtime.items())),
    "confidence_nrt_vs_sp": {f"{a}->{b}": n for (a, b), n in sorted(conf.items())},
    "daynight_nrt_vs_sp": {f"{a}->{b}": n for (a, b), n in sorted(dn.items())},
    "days": len(per_day), "days_nrt_only": sum(1 for _, n, s in per_day if n and not s), "days_sp_only": sum(1 for _, n, s in per_day if s and not n),
    "daily_ratio_nrt_over_sp": q(ratio[~np.isnan(ratio)], [5, 50, 95]),
    "worst_days_abs_diff": sorted(per_day, key=lambda x: -abs(x[1] - x[2]))[:10],
}
(OUT / "nrt_vs_sp.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1)[:4000])
