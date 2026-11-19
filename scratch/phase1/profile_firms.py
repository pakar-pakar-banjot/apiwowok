"""P1-03/04/05/07: profile downloaded FIRMS CSVs. Requires coord_assign.csv from pip_assign.py.
Outputs JSON + CSV tables in data/firms/profile/. Facts only; no fabricated values."""
import pathlib, csv, json, collections, datetime as dt
import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "firms" / "raw"
OUT = REPO / "data" / "firms" / "profile"
TZ = {}  # KDPPUM -> UTC offset hours (WIB/WITA/WIT)
for c in "11 12 13 14 15 16 17 18 19 21 31 32 33 34 35 36 61 62".split():
    TZ[c] = 7
for c in "51 52 53 63 64 65 71 72 73 74 75 76".split():
    TZ[c] = 8
for c in "81 82 91 92 93 94 95 96".split():
    TZ[c] = 9

assign = {}
with open(OUT / "coord_assign.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        assign[(r["latitude"], r["longitude"])] = (r["kdppum"], r["wadmpr"], r["nearest_km"])

NUM = ["latitude", "longitude", "bright_ti4", "scan", "track", "bright_ti5", "frp"]
CAT = ["satellite", "instrument", "confidence", "version", "daynight", "type"]


def pct(a, qs):
    return {f"p{q}": round(float(np.percentile(a, q)), 3) for q in qs} if len(a) else {}


def dist_bin(nk):
    if nk == "":
        return ">11km_or_none"
    x = float(nk)
    if x <= 0.5:
        return "<=0.5km"
    if x <= 1:
        return "<=1km"
    if x <= 2:
        return "<=2km"
    if x <= 5:
        return "<=5km"
    return "5-11km"


report = {}
daily_rows = []
provmonth = collections.Counter()
provday = collections.Counter()

for sdir in sorted(p for p in RAW.iterdir() if p.is_dir()):
    src = sdir.name
    files = 0; rows = 0; nbytes = 0
    headers = collections.Counter(); empty = collections.Counter(); nonnum = collections.Counter()
    cat = {c: collections.Counter() for c in CAT}
    tlen = collections.Counter(); t_invalid = 0; out_of_window = 0
    nums = {c: [] for c in NUM}
    seen_full = set(); seen_k1 = {}; dup_full = dup_k1 = dup_k1_conflict = 0
    seen_k3 = collections.Counter()
    daily_all = collections.Counter(); daily_idn = collections.Counter()
    granules = collections.defaultdict(set)
    solar = collections.Counter(); localshift = collections.Counter()
    inout = collections.Counter(); type_in = collections.Counter(); conf_dn = collections.Counter()
    frp_idn = []; prov_year = collections.Counter()
    type_sites = {t: collections.Counter() for t in ("1", "2", "3")}
    dmin = dmax = None

    for f in sorted(sdir.glob("*.csv")):
        files += 1; nbytes += f.stat().st_size
        start = dt.date.fromisoformat(f.stem.split("_")[0])
        days = int(f.stem.split("_")[1][:-1])
        wend = start + dt.timedelta(days=days - 1)
        with open(f, encoding="utf-8") as fh:
            rd = csv.reader(fh)
            h = next(rd)
            headers[",".join(h)] += 1
            ix = {c: i for i, c in enumerate(h)}
            for row in rd:
                if not row:
                    continue
                rows += 1
                r = {c: row[i] for c, i in ix.items()}
                for c, v in r.items():
                    if v.strip() == "":
                        empty[c] += 1
                for c in NUM:
                    if c in r:
                        try:
                            nums[c].append(float(r[c]))
                        except ValueError:
                            nonnum[c] += 1
                for c in CAT:
                    if c in r:
                        cat[c][r[c]] += 1
                d = dt.date.fromisoformat(r["acq_date"])
                dmin = d if dmin is None or d < dmin else dmin
                dmax = d if dmax is None or d > dmax else dmax
                if not (start <= d <= wend):
                    out_of_window += 1
                t = r["acq_time"]
                tlen[len(t)] += 1
                hh, mm = int(t) // 100, int(t) % 100
                if hh > 23 or mm > 59:
                    t_invalid += 1
                    hh, mm = min(hh, 23), min(mm, 59)
                full = tuple(row)
                if full in seen_full:
                    dup_full += 1
                else:
                    seen_full.add(full)
                k1 = (r["latitude"], r["longitude"], r["acq_date"], r["acq_time"], r.get("satellite", ""))
                if k1 in seen_k1:
                    dup_k1 += 1
                    dup_k1_conflict += seen_k1[k1] != full
                else:
                    seen_k1[k1] = full
                seen_k3[(r["latitude"], r["longitude"], r["acq_date"])] += 1
                daily_all[r["acq_date"]] += 1
                granules[r["acq_date"]].add(t)
                lon = float(r["longitude"])
                sol = ((hh + mm / 60) + lon / 15) % 24
                solar[(r["daynight"], int(sol))] += 1
                kd, nm, nk = assign.get((r["latitude"], r["longitude"]), ("", "", ""))
                if kd:
                    inout["inside"] += 1
                    daily_idn[r["acq_date"]] += 1
                    utc = dt.datetime.combine(d, dt.time(hh, mm))
                    ld = (utc + dt.timedelta(hours=TZ[kd])).date()
                    localshift[(r["daynight"], ld != d)] += 1
                    provmonth[(src, kd, nm, ld.strftime("%Y-%m"))] += 1
                    provday[(src, kd, ld.isoformat())] += 1
                    prov_year[(kd, nm, ld.year)] += 1
                    conf_dn[(r["daynight"], r["confidence"])] += 1
                    try:
                        frp_idn.append(float(r["frp"]))
                    except ValueError:
                        pass
                    type_in[("inside", r.get("type", "(no field)"))] += 1
                else:
                    b = dist_bin(nk)
                    inout["outside " + b] += 1
                    type_in[("outside " + b, r.get("type", "(no field)"))] += 1
                if r.get("type") in type_sites:
                    type_sites[r["type"]][(round(float(r["latitude"]), 1), round(lon, 1), kd or "OUT")] += 1

    rng = [dmin + dt.timedelta(days=i) for i in range((dmax - dmin).days + 1)] if dmin else []
    for day in rng:
        ds = day.isoformat()
        daily_rows.append([src, ds, daily_all.get(ds, 0), daily_idn.get(ds, 0), len(granules.get(ds, ()))])
    idn_daily = np.array([daily_idn.get(d.isoformat(), 0) for d in rng])
    report[src] = {
        "files": files, "rows": rows, "raw_bytes": nbytes, "bytes_per_row": round(nbytes / max(rows, 1), 1),
        "headers": dict(headers), "acq_date_min": str(dmin), "acq_date_max": str(dmax), "days_in_range": len(rng),
        "days_zero_rows_bbox": sum(1 for d in rng if daily_all.get(d.isoformat(), 0) == 0),
        "days_zero_rows_indonesia": int((idn_daily == 0).sum()) if len(rng) else 0,
        "zero_days_list_bbox": [d.isoformat() for d in rng if daily_all.get(d.isoformat(), 0) == 0][:60],
        "out_of_requested_window": out_of_window, "empty_values": dict(empty), "non_numeric": dict(nonnum),
        "numeric": {c: ({"min": min(v), "max": max(v), **pct(np.array(v), [1, 50, 99])} if v else None) for c, v in nums.items()},
        "categorical": {c: dict(v.most_common(15)) for c, v in cat.items() if v},
        "acq_time_str_len": dict(tlen), "acq_time_invalid_hhmm": t_invalid,
        "dup_full_row": dup_full, "dup_key_lat_lon_date_time_sat": dup_k1, "dup_key_conflicting_values": dup_k1_conflict,
        "same_pixel_same_utc_date_multi_times": sum(1 for v in seen_k3.values() if v > 1),
        "granule_times_per_day": pct(np.array([len(granules.get(d.isoformat(), ())) for d in rng]), [0, 50, 100]),
        "inside_outside": dict(inout),
        "type_by_location": {f"{a}|{b}": n for (a, b), n in sorted(type_in.items())},
        "solar_hour_by_daynight": {f"{a}|{b:02d}": n for (a, b), n in sorted(solar.items())},
        "local_date_differs_from_utc_date": {f"{a}|{b}": n for (a, b), n in sorted(localshift.items())},
        "confidence_by_daynight_idn": {f"{a}|{b}": n for (a, b), n in sorted(conf_dn.items())},
        "frp_idn": ({"n": len(frp_idn), "zero": sum(1 for x in frp_idn if x == 0), **pct(np.array(frp_idn), [50, 90, 99, 100])} if frp_idn else None),
        "national_daily_idn": pct(idn_daily, [50, 90, 99, 100]) if len(rng) else {},
        "prov_year": {f"{a} {b}|{y}": n for (a, b, y), n in sorted(prov_year.items())},
        "type_sites_top": {t: [f"{k[0]},{k[1]},{k[2]}:{n}" for k, n in c.most_common(12)] for t, c in type_sites.items() if c},
    }
    print("profiled", src, rows, flush=True)

(OUT / "profile.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
with open(OUT / "daily_counts.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["source", "acq_date_utc", "rows_bbox", "rows_indonesia", "distinct_acq_time"])
    w.writerows(daily_rows)
with open(OUT / "prov_month.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["source", "kdppum", "wadmpr", "local_month", "rows"])
    for k, n in sorted(provmonth.items()):
        w.writerow([*k, n])
with open(OUT / "prov_day.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["source", "kdppum", "local_date", "rows"])
    for k, n in sorted(provday.items()):
        w.writerow([*k, n])
print("DONE")
