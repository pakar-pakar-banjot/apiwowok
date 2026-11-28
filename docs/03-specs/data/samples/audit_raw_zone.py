"""Audit the canonical event contract against the WHOLE Phase 1 raw zone (A-P3-001).

The 25 samples show each case once; this audit checks that the contract holds for every raw row.

  A. every row -> build_event (region-independent checks) -> reason-code counts (expected: 0 rejections,
     matching 06-data-quality-rules.md); 1 in --full-every events (default 10, by detection_id hash; 1 = all)
     against the schema + rules as OUTSIDE shape
  B. identity: duplicate detection_id per product = DQ-08 counts; same duplicate set as the raw-text natural key
     (A-08); no collision across products, also when truncated to 64 bits (CE-01 alternative)
  C. text forms: acq_time digit counts, coordinate decimals, trailing zeros; DQ-04 bbox and DQ-06 window
  D. region on a deterministic 1% sample (detection_id hash): point-in-polygon, full schema + rules,
     agreement with Phase 1 coord_assign.csv, local-date rollover only at night and by at most one day
  E. MULTI_POLYGON coordinates: are the overlapping polygons in the same province or in different provinces?

Usage: python -I docs/03-specs/data/samples/audit_raw_zone.py --data-dir D:/Kuliah/apiwowok/data
Prints a report; exit 0 when every expectation holds. Takes a few minutes; memory is per product.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
import time
from array import array
from collections import Counter
from datetime import date, timedelta

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_samples as bs
import canonical_event as ce
import validate_samples as vs

BBOX = (94.0, -11.5, 141.5, 6.5)  # W,S,E,N of the Phase 1 extraction (DQ-04)
EXPECTED_DQ08 = {"VIIRS_NOAA20_SP": 0, "VIIRS_NOAA21_SP": 1, "VIIRS_NOAA20_NRT": 1, "VIIRS_NOAA21_NRT": 0}
SAMPLE_MOD = 100  # 1% region sample


def all_hits(lon: np.ndarray, lat: np.ndarray, parts) -> list[list[int]]:
    out = [[] for _ in range(len(lon))]
    for fi, e, (x0, y0, x1, y1) in parts:
        idx = np.where((lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1))[0]
        if len(idx) == 0:
            continue
        X, Y = lon[idx, None], lat[idx, None]
        ax, ay, bx, by = e[:, 0], e[:, 1], e[:, 2], e[:, 3]
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (bx - ax) * (Y - ay) / (by - ay) + ax
        inside = (np.count_nonzero(((ay > Y) != (by > Y)) & (X < xint), axis=1) % 2) == 1
        for i in idx[inside]:
            out[i].append(fi)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=pathlib.Path)
    ap.add_argument(
        "--full-every",
        type=int,
        default=10,
        help="run the (slow, pure-Python) schema+rules check on 1 in N rows, chosen by detection_id hash; 1 = all",
    )
    args = ap.parse_args()
    data = args.data_dir.resolve()
    n_full = 0
    t0 = time.time()
    schema = json.loads(vs.SCHEMA.read_text(encoding="utf-8"))
    bdir = data / "boundaries" / bs.BOUNDARY_DIR
    problems: list[str] = []
    if bs.boundary_sha256(bdir) != bs.BOUNDARY_SHA256:
        problems.append("boundary checksum mismatch")
    manifest = {}
    with open(data / "firms" / "manifest.csv", encoding="utf-8", newline="") as fh:
        for m in csv.DictReader(fh):
            manifest[m["file"].removeprefix("raw/")] = m

    total, rejected = 0, Counter()
    schema_fail, rules_fail = [], []
    time_len, lat_dec, trailing_zero, out_bbox, out_window = Counter(), Counter(), 0, 0, 0
    prefixes = array("Q")
    sample = []  # (src, rel, line, row)
    dup_report = {}
    for src in sorted(ce.SOURCES):
        seen_id: dict[bytes, int] = {}
        seen_raw: set[bytes] = set()
        dup_ids, dup_raw = [], 0
        files = sorted((data / "firms" / "raw" / src).glob("*.csv"))
        rows_by_ref = {}
        for fidx, f in enumerate(files):
            rel = f"{src}/{f.name}"
            m = manifest[rel]
            w0 = date.fromisoformat(m["start"])
            w1 = w0 + timedelta(days=int(m["days"]))
            prov = {"source_file": rel, "source_file_sha256": m["sha256"],
                    "fetched_at_utc": ce.normalize_utc_timestamp(m["fetched_at_utc"]), "ingest_run_id": "audit"}  # fmt: skip
            with open(f, encoding="utf-8", newline="") as fh:
                for line, row in enumerate(csv.DictReader(fh), start=2):
                    total += 1
                    time_len[len(row["acq_time"])] += 1
                    la = row["latitude"]
                    lat_dec[len(la.split(".")[1]) if "." in la else 0] += 1
                    for c in (row["latitude"], row["longitude"]):
                        if "." in c and c.endswith("0"):
                            trailing_zero += 1
                    try:
                        ev = ce.build_event(src, row, None, bs.BOUNDARY_VERSION, prov)
                    except ce.RowRejected as x:
                        rejected[(src, x.code)] += 1
                        continue
                    if not (BBOX[1] <= ev["latitude"] <= BBOX[3] and BBOX[0] <= ev["longitude"] <= BBOX[2]):
                        out_bbox += 1
                    if not (w0 <= date.fromisoformat(ev["source_acq_date_utc"]) < w1):
                        out_window += 1
                    dig = bytes.fromhex(ev["detection_id"])
                    if int.from_bytes(dig[:4], "big") % args.full_every == 0:
                        n_full += 1
                        if vs.schema_errors(ev, schema):
                            schema_fail.append((rel, line))
                        if vs.rule_errors(ev):
                            rules_fail.append((rel, line))
                    ref = fidx * 10_000_000 + line
                    if dig[:16] in seen_id:
                        dup_ids.append((seen_id[dig[:16]], ref, ev["detection_id"]))
                    else:
                        seen_id[dig[:16]] = ref
                    raw_key = "|".join(row[k] for k in ("latitude", "longitude", "acq_date", "acq_time", "satellite"))
                    rk = hashlib.sha256(raw_key.encode()).digest()[:16]
                    if rk in seen_raw:
                        dup_raw += 1
                    else:
                        seen_raw.add(rk)
                    prefixes.append(int.from_bytes(dig[:8], "big"))
                    if int.from_bytes(dig[-4:], "big") % SAMPLE_MOD == 0:
                        sample.append((src, rel, line, row))
        # fetch the rows of duplicate pairs to classify identical vs conflicting values
        need = {r for a, b, _ in dup_ids for r in (a, b)}
        for fidx, f in enumerate(files):
            if not any(r // 10_000_000 == fidx for r in need):
                continue
            with open(f, encoding="utf-8", newline="") as fh:
                for line, row in enumerate(csv.DictReader(fh), start=2):
                    if fidx * 10_000_000 + line in need:
                        rows_by_ref[fidx * 10_000_000 + line] = (f"{src}/{f.name}", line, row)
        pairs = []
        for a, b, did in dup_ids:
            ra, rb = rows_by_ref[a], rows_by_ref[b]
            diff = [k for k in ra[2] if ra[2][k] != rb[2][k]]
            pairs.append({"detection_id": did[:12], "a": f"{ra[0]}:{ra[1]}", "b": f"{rb[0]}:{rb[1]}", "differs": diff})
        dup_report[src] = {"dup_ids": len(dup_ids), "dup_raw_key": dup_raw, "pairs": pairs}
        if len(dup_ids) != EXPECTED_DQ08[src]:
            problems.append(f"{src}: {len(dup_ids)} duplicate detection_id, DQ-08 expects {EXPECTED_DQ08[src]}")
        if len(dup_ids) != dup_raw:
            problems.append(f"{src}: detection_id duplicates {len(dup_ids)} != raw-key duplicates {dup_raw}")
        del seen_id, seen_raw
        print(f"  {src}: done ({time.time() - t0:.0f}s)", flush=True)

    arr = np.frombuffer(prefixes, dtype=np.uint64)
    n_dup_rows = sum(v["dup_ids"] for v in dup_report.values())
    uniq64 = len(np.unique(arr))
    if uniq64 != len(arr) - n_dup_rows:
        problems.append(f"64-bit prefix collisions: {len(arr) - n_dup_rows - uniq64}")
    if rejected:
        problems.append(f"rejections: {dict(rejected)}")
    if schema_fail or rules_fail:
        problems.append(
            f"schema failures {len(schema_fail)}, rule failures {len(rules_fail)}: {(schema_fail + rules_fail)[:3]}"
        )
    if out_bbox or out_window:
        problems.append(f"outside bbox {out_bbox}, outside request window {out_window}")

    # D. region sample
    feats, parts = bs.load_polygons(bdir)
    lon = np.array([float(s[3]["longitude"]) for s in sample])
    lat = np.array([float(s[3]["latitude"]) for s in sample])
    first, hits = bs.point_in_polygons(lon, lat, parts)
    region_stats, cross = Counter(), Counter()
    want = {}
    for (src, rel, line, row), fi, nh in zip(sample, first, hits):
        m = manifest[rel]
        prov = {"source_file": rel, "source_file_sha256": m["sha256"],
                "fetched_at_utc": ce.normalize_utc_timestamp(m["fetched_at_utc"]), "ingest_run_id": "audit"}  # fmt: skip
        region = None if fi < 0 else (feats[fi]["properties"]["KDPPUM"], feats[fi]["properties"]["WADMPR"], int(nh))
        ev = ce.build_event(src, row, region, bs.BOUNDARY_VERSION, prov)
        if vs.schema_errors(ev, schema) or vs.rule_errors(ev):
            problems.append(f"region sample invalid: {rel}:{line}")
        region_stats[ev["region_status"]] += 1
        if "MULTI_POLYGON" in ev["dq_flags"]:
            region_stats["MULTI_POLYGON"] += 1
        if ev["region_status"] == "INSIDE":
            delta = (date.fromisoformat(ev["local_date"]) - date.fromisoformat(ev["source_acq_date_utc"])).days
            cross[(ev["local_tz"], ev["daynight"], delta)] += 1
            if delta not in (0, 1) or (delta == 1 and ev["daynight"] != "N"):
                problems.append(f"unexpected local-date shift {delta} ({ev['daynight']}) at {rel}:{line}")
        want[(row["latitude"], row["longitude"])] = (region[0] if region else "", int(nh))
    seen, multi = {}, []
    with open(data / "firms" / "profile" / "coord_assign.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            k = (r["latitude"], r["longitude"])
            if k in want:
                seen[k] = (r["kdppum"], int(r["n_hits"]))
            if r["n_hits"] not in ("0", "1"):
                multi.append(k)
    disagree = [k for k, v in want.items() if seen.get(k) != v]
    if disagree:
        problems.append(f"region disagrees with coord_assign.csv for {len(disagree)} coords, e.g. {disagree[:2]}")

    # E. multi-polygon coordinates
    hl = all_hits(np.array([float(b) for _, b in multi]), np.array([float(a) for a, _ in multi]), parts)
    same_prov = sum(1 for h in hl if len({feats[i]["properties"]["KDPPUM"] for i in h}) == 1)
    cross_prov = [
        (multi[j], sorted({feats[i]["properties"]["KDPPUM"] for i in h}))
        for j, h in enumerate(hl)
        if len({feats[i]["properties"]["KDPPUM"] for i in h}) > 1
    ]

    print("\n=== audit_raw_zone ===")
    print(f"rows: {total}  rejected: {sum(rejected.values())} {dict(rejected) or ''}")
    print(
        f"[A] build_event on every row; schema+rules on {n_full} rows (1 in {args.full_every}, OUTSIDE shape): "
        f"schema fail {len(schema_fail)}, rules fail {len(rules_fail)}"
    )
    for src, v in dup_report.items():
        print(f"[B] {src}: duplicate detection_id {v['dup_ids']} (DQ-08 expects {EXPECTED_DQ08[src]}), "
              f"raw-key duplicates {v['dup_raw_key']}; pairs {v['pairs']}")  # fmt: skip
    print(f"[B] 64-bit prefix: {len(arr)} ids, {uniq64} unique (= ids - duplicates: {uniq64 == len(arr) - n_dup_rows})")
    print(f"[C] acq_time digits {dict(sorted(time_len.items()))}; latitude decimals {dict(sorted(lat_dec.items()))}; "
          f"coordinate texts with trailing zero {trailing_zero}; outside bbox {out_bbox}; outside window {out_window}")  # fmt: skip
    print(
        f"[D] region sample {len(sample)} rows: {dict(region_stats)}; agree with coord_assign {len(want) - len(disagree)}/{len(want)}"
    )
    print(f"[D] INSIDE (zone, daynight, local-UTC days): {dict(sorted(cross.items()))}")
    print(
        f"[E] multi-polygon coords {len(multi)}: same province {same_prov}, different provinces {len(cross_prov)} {cross_prov[:5]}"
    )
    print(f"time {time.time() - t0:.0f}s")
    print("PROBLEMS:", problems or "none")
    print("RESULT:", "FAIL" if problems else "PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
