"""Build canonical-events.sample.jsonl from the Phase 1 raw zone (A-P3-001).

Deterministic: files are read in sorted order, candidates are kept in file/line order, and each required case
takes the first candidate that satisfies it. Re-running with the same raw zone gives byte-identical output.

Usage (data/ is git-ignored and lives in the main checkout):
    python -I docs/03-specs/data/samples/build_samples.py --data-dir D:/Kuliah/apiwowok/data

Reads: <data>/firms/manifest.csv, <data>/firms/raw/*/*.csv, <data>/boundaries/big_kabkota_2026_06_off0.001/*.geojson
Writes (next to this script): canonical-events.sample.jsonl, canonical-events.sample.cases.csv
Needs numpy (already used by scratch/phase1/pip_assign.py); no new dependency.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import canonical_event as ce

BOUNDARY_DIR = "big_kabkota_2026_06_off0.001"
BOUNDARY_SHA256 = "0382eeeeb559991a41dbb9ba84d593740c4cea7614703f4c2a93d10495f3e478"  # 05-boundary-sources §4
BOUNDARY_VERSION = "BIG-2026-06-g0.001-" + BOUNDARY_SHA256[:12]
SAMPLE_RUN_ID = "sample-A-P3-001"  # ILUSTRASI: samples are not produced by an ingest run
PER_BUCKET = 25


def boundary_sha256(bdir: pathlib.Path) -> str:
    h = hashlib.sha256()
    for p in sorted(bdir.glob("*.geojson")):
        h.update(p.read_bytes())
    return h.hexdigest()


def load_polygons(bdir: pathlib.Path):
    feats = []
    for p in sorted(bdir.glob("*.geojson")):
        feats += json.loads(p.read_text(encoding="utf-8"))["features"]
    parts = []
    for i, f in enumerate(feats):
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            e = np.vstack(
                [
                    np.hstack([np.asarray(r, dtype=np.float64)[:-1, :2], np.asarray(r, dtype=np.float64)[1:, :2]])
                    for r in poly
                ]
            )
            parts.append((i, e, (e[:, [0, 2]].min(), e[:, [1, 3]].min(), e[:, [0, 2]].max(), e[:, [1, 3]].max())))
    return feats, parts


def point_in_polygons(lon: np.ndarray, lat: np.ndarray, parts):
    """Even-odd ray casting, same algorithm and feature order as scratch/phase1/pip_assign.py."""
    first = np.full(len(lon), -1, dtype=np.int64)
    hits = np.zeros(len(lon), dtype=np.int32)
    for fi, e, (x0, y0, x1, y1) in parts:
        idx = np.where((lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1))[0]
        if len(idx) == 0:
            continue
        X, Y = lon[idx, None], lat[idx, None]
        ax, ay, bx, by = e[:, 0], e[:, 1], e[:, 2], e[:, 3]
        cross = (ay > Y) != (by > Y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (bx - ax) * (Y - ay) / (by - ay) + ax
        inside = (np.count_nonzero(cross & (X < xint), axis=1) % 2) == 1
        h = idx[inside]
        hits[h] += 1
        first[h] = np.where(first[h] < 0, fi, first[h])
    return first, hits


def bucket(source: str, row: dict) -> tuple:
    t = row["acq_time"].zfill(4)
    hour = int(t[:2])
    lon = float(row["longitude"])
    return (
        source,
        row["daynight"],
        "day"
        if row["daynight"] == "D"
        else ("15" if hour == 15 else "16" if hour == 16 else "17+" if hour >= 17 else "<15"),
        row["confidence"],
        row.get("type", ""),
        float(row["frp"]) == 0.0,
        float(row["bright_ti4"]) == ce.TI4_SATURATION_K,
        0 if lon < 115 else 1 if lon < 125 else 2,
    )


# Required cases, in selection order. Each takes the first not-yet-used candidate satisfying the predicate.
def _crosses(e):
    return e["region_status"] == "INSIDE" and e["local_date"] != e["source_acq_date_utc"]


CASES = []
for src in ce.SOURCES:
    CASES += [
        (
            f"{src}: INSIDE siang",
            lambda e, s=src: e["source_id"] == s and e["region_status"] == "INSIDE" and e["daynight"] == "D",
        ),
        (f"{src}: INSIDE malam, tanggal lokal ≠ tanggal UTC", lambda e, s=src: e["source_id"] == s and _crosses(e)),
        (
            f"{src}: OUTSIDE (di luar 38 provinsi)",
            lambda e, s=src: e["source_id"] == s and e["region_status"] == "OUTSIDE",
        ),
    ]
CASES += [
    ("WIB malam, lintas tanggal (UTC ≥ 17:00)", lambda e: _crosses(e) and e["local_tz"] == "WIB"),
    ("WITA malam, lintas tanggal (UTC ≥ 16:00)", lambda e: _crosses(e) and e["local_tz"] == "WITA"),
    ("WIT malam, lintas tanggal (UTC ≥ 15:00)", lambda e: _crosses(e) and e["local_tz"] == "WIT"),
    (
        "WIB malam, tanggal lokal = tanggal UTC (UTC < 17:00)",
        lambda e: e["local_tz"] == "WIB" and e["daynight"] == "N" and not _crosses(e),
    ),
    ("WITA siang", lambda e: e["local_tz"] == "WITA" and e["daynight"] == "D"),
    ("WIT siang", lambda e: e["local_tz"] == "WIT" and e["daynight"] == "D"),
    ("SP type 1 (gunung api) → NON_VEGETATION_TYPE", lambda e: e["type"] == 1 and e["region_status"] == "INSIDE"),
    (
        "SP type 2 (sumber statis darat) → NON_VEGETATION_TYPE",
        lambda e: e["type"] == 2 and e["region_status"] == "INSIDE",
    ),
    ("SP type 3 (offshore) → NON_VEGETATION_TYPE", lambda e: e["type"] == 3),
    (
        "confidence h + bright_ti4 = 367 K → TI4_SATURATED",
        lambda e: e["confidence_raw"] == "h" and "TI4_SATURATED" in e["dq_flags"],
    ),
    ("confidence l (low)", lambda e: e["confidence_raw"] == "l" and e["region_status"] == "INSIDE"),
    ("frp = 0 → FRP_ZERO", lambda e: "FRP_ZERO" in e["dq_flags"]),
    ("titik di >1 poligon → MULTI_POLYGON (poligon pertama)", lambda e: "MULTI_POLYGON" in e["dq_flags"]),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=pathlib.Path)
    args = ap.parse_args()
    data = args.data_dir.resolve()
    bdir = data / "boundaries" / BOUNDARY_DIR

    got = boundary_sha256(bdir)
    if got != BOUNDARY_SHA256:
        print(f"boundary checksum mismatch: {got}", file=sys.stderr)
        return 1
    manifest = {}
    with open(data / "firms" / "manifest.csv", encoding="utf-8", newline="") as fh:
        for m in csv.DictReader(fh):
            manifest[m["file"].removeprefix("raw/")] = m

    # 0. Hint for the rare MULTI_POLYGON case (DQ-07b, ~100 of 2.7M rows): coordinates that Phase 1
    #    (scratch/phase1/pip_assign.py) found in >1 polygon. Only used to pick candidates; the region of every
    #    sample is recomputed below.
    multi = set()
    with open(data / "firms" / "profile" / "coord_assign.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["n_hits"] not in ("0", "1"):
                multi.add((r["latitude"], r["longitude"]))
    print(f"phase-1 multi-polygon coordinates: {len(multi)}")
    n_multi = 0

    # 1. Candidates: first PER_BUCKET rows of each bucket, in sorted file / line order.
    buckets: dict[tuple, int] = {}
    cand = []  # (source_id, rel_file, line_no, row)
    n_rows = 0
    for src in sorted(ce.SOURCES):
        for f in sorted((data / "firms" / "raw" / src).glob("*.csv")):
            rel = f"{src}/{f.name}"
            with open(f, encoding="utf-8", newline="") as fh:
                rd = csv.DictReader(fh)
                for line_no, row in enumerate(rd, start=2):
                    n_rows += 1
                    k = bucket(src, row)
                    if buckets.get(k, 0) < PER_BUCKET:
                        buckets[k] = buckets.get(k, 0) + 1
                        cand.append((src, rel, line_no, row))
                    elif n_multi < PER_BUCKET and (row["latitude"], row["longitude"]) in multi:
                        n_multi += 1
                        cand.append((src, rel, line_no, row))
    print(f"raw rows scanned: {n_rows}; buckets: {len(buckets)}; candidates: {len(cand)}")

    # 2. Region for candidates only.
    feats, parts = load_polygons(bdir)
    lon = np.array([float(c[3]["longitude"]) for c in cand])
    lat = np.array([float(c[3]["latitude"]) for c in cand])
    first, hits = point_in_polygons(lon, lat, parts)

    events = []
    for (src, rel, line_no, row), fi, nh in zip(cand, first, hits):
        m = manifest[rel]
        region = None
        if fi >= 0:
            p = feats[fi]["properties"]
            region = (p["KDPPUM"], p["WADMPR"], int(nh))
        prov = {
            "source_file": rel,
            "source_file_sha256": m["sha256"],
            "fetched_at_utc": m["fetched_at_utc"].replace("+00:00", "Z"),
            "ingest_run_id": SAMPLE_RUN_ID,
        }
        events.append((ce.build_event(src, row, region, BOUNDARY_VERSION, prov), rel, line_no))

    # 3. Select one candidate per case.
    used, out = set(), []
    for name, pred in CASES:
        pick = next(((e, rel, ln) for e, rel, ln in events if e["detection_id"] not in used and pred(e)), None)
        if pick is None:
            print(f"NO CANDIDATE for case: {name}", file=sys.stderr)
            return 1
        used.add(pick[0]["detection_id"])
        out.append((name, *pick))

    with open(HERE / "canonical-events.sample.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        fh.writelines(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for _, e, _, _ in out)
    with open(HERE / "canonical-events.sample.cases.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["n", "case", "detection_id", "source_file", "source_line"])
        for i, (name, e, rel, ln) in enumerate(out, start=1):
            w.writerow([i, name, e["detection_id"], rel, ln])
    print(f"samples written: {len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
