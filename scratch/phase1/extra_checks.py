"""P1-03/04/05/09 + B-P1-001: extra measurements on the Phase 1 raw zone and profile outputs.
Reads data/firms/raw, data/firms/profile/{coord_assign,prov_day,prov_month}.csv, data/firms/missing_data.json.
Writes data/firms/profile/extra_checks.json. Facts only."""
import pathlib, csv, json, re, collections, datetime as dt
import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "firms" / "raw"; PROF = REPO / "data" / "firms" / "profile"
OUT = {}

# 1. value-level checks per source
assign = {}
with open(PROF / "coord_assign.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        assign[(r["latitude"], r["longitude"])] = (r["kdppum"], r["n_hits"], r["nearest_km"])
chk = {}
for sdir in sorted(p for p in RAW.iterdir() if p.is_dir()):
    c = collections.Counter()
    for f in sorted(sdir.glob("*.csv")):
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                c["rows"] += 1
                ti4, ti5, frp = float(r["bright_ti4"]), float(r["bright_ti5"]), float(r["frp"])
                c["ti4_eq_367"] += ti4 == 367.0
                c["ti4_lt_ti5"] += ti4 < ti5
                c["ti4_lt_280"] += ti4 < 280
                c["frp_eq_0"] += frp == 0
                c["frp_gt_500"] += frp > 500
                if r["daynight"] == "N" and r["confidence"] == "l":
                    c["night_low_conf"] += 1
                kd, nh, nk = assign.get((r["latitude"], r["longitude"]), ("", "0", ""))
                c["multi_polygon_hit"] += int(nh or 0) > 1
                if r["confidence"] == "h":
                    c["conf_h_and_ti4_367"] += ti4 == 367.0
                c[f"type_{r.get('type', 'none')}"] += 1
    chk[sdir.name] = dict(c)
OUT["value_checks"] = chk

# 2. zero-data days vs FIRMS missing_data table (rows: date, satellite)
html = json.loads((REPO / "data" / "firms" / "missing_data.json").read_text(encoding="utf-8"))["html"]
cells = re.findall(r"<td>(.*?)</td>", html)
pairs = [(cells[i], cells[i + 1]) for i in range(0, len(cells) - 1, 2)]
miss = collections.defaultdict(set)
for d, s in pairs:
    if re.match(r"\d{4}-\d{2}-\d{2}$", d):
        miss[s].add(d)
OUT["missing_data_satellites"] = {s: len(v) for s, v in miss.items()}
daily = collections.defaultdict(dict)
with open(PROF / "daily_counts.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        daily[r["source"]][r["acq_date_utc"]] = (int(r["rows_bbox"]), int(r["rows_indonesia"]))
satname = {"VIIRS_NOAA20": "NOAA-20 (VIIRS)", "VIIRS_NOAA21": "NOAA-21 (VIIRS)"}
zd = {}
for src, dd in daily.items():
    listed = miss.get(satname[src.rsplit("_", 1)[0]], set())
    lo, hi = min(dd), max(dd)
    listed_in = sorted(d for d in listed if lo <= d <= hi)
    zero_bbox = sorted(d for d, (b, i) in dd.items() if b == 0)
    zero_idn_only = sorted(d for d, (b, i) in dd.items() if b > 0 and i == 0)
    zd[src] = {"listed_missing_in_range": listed_in, "zero_rows_bbox": zero_bbox,
               "zero_but_not_listed": sorted(set(zero_bbox) - set(listed_in)),
               "listed_but_has_rows": [(d, dd[d][0]) for d in listed_in if dd.get(d, (0, 0))[0] > 0],
               "zero_in_indonesia_only": [(d, dd[d][0]) for d in zero_idn_only]}
OUT["zero_days"] = zd

# 3. province coverage and per-partition volumes
pd_rows = collections.defaultdict(list)   # (source) -> list of rows per province-local day
pd_comb = collections.Counter()           # (kd, local_date) -> rows, SP(<=2026-07-31) + NRT(>=2026-08-01), N20+N21
prov_tot = collections.Counter(); provs = set()
with open(PROF / "prov_day.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        n = int(r["rows"]); src = r["source"]; d = r["local_date"]
        pd_rows[src].append(n); provs.add(r["kdppum"])
        sp = src.endswith("_SP")
        if (sp and d <= "2026-07-31") or (not sp and d >= "2026-08-01"):
            pd_comb[(r["kdppum"], d)] += n
            prov_tot[r["kdppum"]] += n
q = lambda a: {"n": len(a), "p50": float(np.percentile(a, 50)), "p90": float(np.percentile(a, 90)),
               "p99": float(np.percentile(a, 99)), "max": int(max(a))} if len(a) else {}
OUT["provinces_seen"] = sorted(provs)
OUT["province_day_rows_by_source"] = {s: q(v) for s, v in pd_rows.items()}
OUT["province_day_rows_combined"] = q(list(pd_comb.values()))
top = sorted(pd_comb.items(), key=lambda kv: -kv[1])[:10]
OUT["province_day_top10_combined"] = [f"{k[0]} {k[1]}: {v}" for k, v in top]
pm = collections.Counter()
for (kd, d), n in pd_comb.items():
    pm[(kd, d[:7])] += n
OUT["province_month_rows_combined"] = q(list(pm.values()))
OUT["province_month_top10_combined"] = [f"{k[0]} {k[1]}: {v}" for k, v in sorted(pm.items(), key=lambda kv: -kv[1])[:10]]
nat = collections.Counter()
for (kd, d), n in pd_comb.items():
    nat[d] += n
OUT["national_day_rows_combined"] = q(list(nat.values()))
OUT["combined_total_rows_inside"] = sum(pd_comb.values())
OUT["combined_rows_by_province"] = dict(sorted(prov_tot.items()))
# days with zero rows for a province are not partitions; report share of province-days with data
days_span = (dt.date(2026, 11, 18) - dt.date(2023, 1, 1)).days + 1
OUT["province_days_with_data_share"] = round(len(pd_comb) / (len(provs) * days_span), 3)

(PROF / "extra_checks.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8")
print(json.dumps(OUT, indent=1)[:9000])
