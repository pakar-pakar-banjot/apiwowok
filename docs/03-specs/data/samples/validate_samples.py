"""Validate canonical-events.sample.jsonl (A-P3-001).

Checks, in order:
  [schema]   every record against canonical-event.schema.json (JSON Schema 2020-12 subset, stdlib only;
             unknown keywords are an error, so nothing is silently skipped)
  [rules]    contract rules a schema cannot express (detection_id, local date, zone, flags, source mapping, uniqueness)
  [coverage] the sample mix required by 06-interface-contracts §B and the A-P3-001 task card
  [selftest] mutated records must be rejected (negative tests) + order-independence of detection_id
  [trace]    (only with --data-dir) each record equals a rebuild from its raw CSV line; file SHA-256 = manifest =
             actual file; boundary snapshot checksum; region agrees with Phase 1 coord_assign.csv

Usage:
    python -I docs/03-specs/data/samples/validate_samples.py [--data-dir D:/Kuliah/apiwowok/data]
Exit 0 = all checks passed.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import pathlib
import random
import re
import sys
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import canonical_event as ce

SAMPLES = HERE / "canonical-events.sample.jsonl"
CASES = HERE / "canonical-events.sample.cases.csv"
SCHEMA = HERE / "canonical-event.schema.json"

# ---------------------------------------------------------------- JSON Schema subset (2020-12)
_ANNOTATIONS = {"$schema", "$id", "title", "description"}
_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: (isinstance(v, int) and not isinstance(v, bool)) or (isinstance(v, float) and v.is_integer()),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _json_eq(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if a is None or b is None:
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    return type(a) is type(b) and a == b


def schema_errors(inst, sch, path="$"):
    errs = []
    for k in sch:
        if k not in _ANNOTATIONS and not k.startswith("x-") and k not in _KEYWORDS:
            raise ValueError(f"unsupported schema keyword {k!r} at {path}")
    if "type" in sch:
        ts = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(_TYPES[t](inst) for t in ts):
            return [f"{path}: type {type(inst).__name__} not in {ts}"]
    if "enum" in sch and not any(_json_eq(inst, e) for e in sch["enum"]):
        errs.append(f"{path}: {inst!r} not in enum")
    if "const" in sch and not _json_eq(inst, sch["const"]):
        errs.append(f"{path}: {inst!r} != const {sch['const']!r}")
    if isinstance(inst, str):
        if "pattern" in sch and not re.search(sch["pattern"], inst):
            errs.append(f"{path}: {inst!r} !~ /{sch['pattern']}/")
        if "minLength" in sch and len(inst) < sch["minLength"]:
            errs.append(f"{path}: shorter than {sch['minLength']}")
        if "maxLength" in sch and len(inst) > sch["maxLength"]:
            errs.append(f"{path}: longer than {sch['maxLength']}")
    if _TYPES["number"](inst):
        if "minimum" in sch and inst < sch["minimum"]:
            errs.append(f"{path}: {inst} < {sch['minimum']}")
        if "maximum" in sch and inst > sch["maximum"]:
            errs.append(f"{path}: {inst} > {sch['maximum']}")
        if "exclusiveMinimum" in sch and inst <= sch["exclusiveMinimum"]:
            errs.append(f"{path}: {inst} <= {sch['exclusiveMinimum']}")
    if isinstance(inst, dict):
        for r in sch.get("required", []):
            if r not in inst:
                errs.append(f"{path}: missing {r!r}")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += schema_errors(v, props[k], f"{path}.{k}")
            elif sch.get("additionalProperties") is False:
                errs.append(f"{path}: unexpected property {k!r}")
    if isinstance(inst, list):
        if "items" in sch:
            for i, v in enumerate(inst):
                errs += schema_errors(v, sch["items"], f"{path}[{i}]")
        if sch.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in inst}) != len(inst):
            errs.append(f"{path}: items not unique")
    for i, sub in enumerate(sch.get("allOf", [])):
        errs += schema_errors(inst, sub, f"{path}/allOf[{i}]")
    if "if" in sch:
        branch = "then" if not schema_errors(inst, sch["if"], path) else "else"
        if branch in sch:
            errs += schema_errors(inst, sch[branch], f"{path}/{branch}")
    return errs


_KEYWORDS = {
    "type",
    "enum",
    "const",
    "pattern",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "uniqueItems",
    "allOf",
    "if",
    "then",
    "else",
}


# ---------------------------------------------------------------- contract rules
def rule_errors(e: dict) -> list[str]:
    errs = []
    try:
        dt = datetime.strptime(e["acq_datetime_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ce.UTC)
    except (KeyError, ValueError, TypeError) as x:
        return [f"acq_datetime_utc unparsable: {x}"]
    sat, level, version = ce.SOURCES.get(e.get("source_id"), (None, None, None))
    if (e.get("satellite"), e.get("processing_level"), e.get("version_raw")) != (sat, level, version):
        errs.append("satellite/processing_level/version_raw do not match source_id")
    want_id = ce.detection_id(e["processing_level"], e["satellite"], dt, repr(e["latitude"]), repr(e["longitude"]))
    if e.get("detection_id") != want_id:
        errs.append("detection_id != SHA-256 of identity string")
    if e.get("source_acq_date_utc") != dt.date().isoformat():
        errs.append("source_acq_date_utc != date(acq_datetime_utc)")
    if e.get("region_status") == "INSIDE":
        zone = ce.PROVINCE_ZONE.get(e.get("province_code"))
        if e.get("local_tz") != zone:
            errs.append(f"local_tz {e.get('local_tz')} != zone of province {e.get('province_code')} ({zone})")
        elif e.get("local_date") != ce.local_date(dt, zone):
            errs.append("local_date != date(acq_datetime_utc + zone offset)")
    flags = e.get("dq_flags", [])
    want = set(ce.dq_flags(e["bright_ti4"], e["frp"], e["type"], 1))
    if set(flags) - {"MULTI_POLYGON"} != want:
        errs.append(f"dq_flags {flags} != row-derived {sorted(want)} (+MULTI_POLYGON from boundary)")
    if "MULTI_POLYGON" in flags and e.get("region_status") != "INSIDE":
        errs.append("MULTI_POLYGON on an OUTSIDE event")
    if flags != sorted(flags):
        errs.append("dq_flags not sorted")
    if not e.get("source_file", "").startswith(e.get("source_id", "?") + "/"):
        errs.append("source_file is not under source_id directory")
    return errs


def coverage_errors(evs: list[dict]) -> list[str]:
    errs = []
    if len(evs) < 20:
        errs.append(f"only {len(evs)} samples (< 20)")
    crosses = [e for e in evs if e["region_status"] == "INSIDE" and e["local_date"] != e["source_acq_date_utc"]]
    need = {
        "SP": any(e["processing_level"] == "SP" for e in evs),
        "NRT": any(e["processing_level"] == "NRT" for e in evs),
        "NOAA-20": any(e["satellite"] == "N20" for e in evs),
        "NOAA-21": any(e["satellite"] == "N21" for e in evs),
        "OUTSIDE": any(e["region_status"] == "OUTSIDE" for e in evs),
        "malam lintas tanggal lokal": bool(crosses),
        "lintas tanggal di WIB, WITA, WIT": {e["local_tz"] for e in crosses} >= {"WIB", "WITA", "WIT"},
        "setiap source_id": {e["source_id"] for e in evs} == set(ce.SOURCES),
        "type null (NRT) dan type 0..3 (SP)": {e["type"] for e in evs} >= {None, 0, 1, 2, 3},
        "confidence l, n, h": {e["confidence_raw"] for e in evs} == {"l", "n", "h"},
        "setiap dq_flag": {f for e in evs for f in e["dq_flags"]} == set(ce.DQ_FLAGS),
    }
    errs += [f"coverage missing: {k}" for k, ok in need.items() if not ok]
    if len({e["detection_id"] for e in evs}) != len(evs):
        errs.append("duplicate detection_id in samples")
    return errs, need


def selftest(evs: list[dict], schema: dict) -> list[str]:
    base_inside = next(e for e in evs if e["region_status"] == "INSIDE" and e["processing_level"] == "NRT")
    base_outside = next(e for e in evs if e["region_status"] == "OUTSIDE")
    base_sp = next(e for e in evs if e["processing_level"] == "SP" and e["region_status"] == "INSIDE")
    other_zone_code = next(c for c, z in ce.PROVINCE_ZONE.items() if z != base_inside["local_tz"])
    mutations = {
        "NRT dengan type 0": (base_inside, {"type": 0}),
        "SP dengan type null": (base_sp, {"type": None}),
        "INSIDE tanpa province_code": (base_inside, {"province_code": None}),
        "OUTSIDE dengan local_date": (base_outside, {"local_date": "2023-01-01"}),
        "detection_id salah": (base_inside, {"detection_id": "0" * 64}),
        "local_date salah": (base_inside, {"local_date": "1999-01-01"}),
        "local_tz tidak sesuai provinsi": (base_inside, {"province_code": other_zone_code}),
        "field tambahan": (base_inside, {"extra": 1}),
        "confidence_class tidak cocok": (base_inside, {"confidence_raw": "h", "confidence_class": "low"}),
        "version_raw tidak cocok": (base_inside, {"version_raw": "2"}),
        "satellite tidak cocok source_id": (
            base_inside,
            {"satellite": "N21" if base_inside["satellite"] == "N20" else "N20"},
        ),
        "dq_flags tidak sesuai nilai": (base_inside, {"frp": 0.0}),
        "acq_datetime tanpa Z": (base_inside, {"acq_datetime_utc": base_inside["acq_datetime_utc"][:-1]}),
        "flag tidak dikenal": (base_inside, {"dq_flags": ["OUTSIDE"]}),
    }
    errs = []
    for name, (base, patch) in mutations.items():
        m = copy.deepcopy(base)
        m.update(patch)
        if not (schema_errors(m, schema) or (_safe_rules(m))):
            errs.append(f"mutation accepted (should be rejected): {name}")
    missing = copy.deepcopy(base_inside)
    del missing["boundary_version"]
    if not schema_errors(missing, schema):
        errs.append("mutation accepted (should be rejected): field wajib hilang")
    ids = [e["detection_id"] for e in evs]
    rng = random.Random(20261126)
    for _ in range(50):
        shuffled = evs[:]
        rng.shuffle(shuffled)
        dt = lambda e: datetime.strptime(e["acq_datetime_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ce.UTC)
        got = [
            ce.detection_id(e["processing_level"], e["satellite"], dt(e), repr(e["latitude"]), repr(e["longitude"]))
            for e in shuffled
        ]
        if set(got) != set(ids):
            errs.append("detection_id set depends on input order")
            break
    if ce.canonical_decimal("-1.50000") != ce.canonical_decimal("-1.5") or ce.canonical_decimal("-0.0") != "0":
        errs.append("canonical_decimal not normalising trailing zeros / negative zero")
    return errs, len(mutations) + 1


def _safe_rules(m):
    try:
        return rule_errors(m)
    except (KeyError, TypeError, ValueError) as x:  # a mutation that breaks rule evaluation is also a rejection
        return [repr(x)]


# ---------------------------------------------------------------- trace to raw zone
def trace_errors(evs: list[dict], data: pathlib.Path) -> list[str]:
    import build_samples as bs  # needs numpy; only for --data-dir

    errs = []
    bdir = data / "boundaries" / bs.BOUNDARY_DIR
    if bs.boundary_sha256(bdir) != bs.BOUNDARY_SHA256:
        errs.append("boundary snapshot checksum != 05-boundary-sources")
    manifest = {}
    with open(data / "firms" / "manifest.csv", encoding="utf-8", newline="") as fh:
        for m in csv.DictReader(fh):
            manifest[m["file"].removeprefix("raw/")] = m
    with open(CASES, encoding="utf-8", newline="") as fh:
        cases = {r["detection_id"]: r for r in csv.DictReader(fh)}
    feats, parts = bs.load_polygons(bdir)
    rows = []
    for e in evs:
        c = cases.get(e["detection_id"])
        if c is None or c["source_file"] != e["source_file"]:
            errs.append(f"{e['detection_id'][:12]}: no matching line in cases.csv")
            rows.append(None)
            continue
        f = data / "firms" / "raw" / e["source_file"]
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        m = manifest[e["source_file"]]
        if not (actual == m["sha256"] == e["source_file_sha256"]):
            errs.append(f"{e['detection_id'][:12]}: source file SHA-256 mismatch (file/manifest/event)")
        if m["fetched_at_utc"].replace("+00:00", "Z") != e["fetched_at_utc"]:
            errs.append(f"{e['detection_id'][:12]}: fetched_at_utc != manifest")
        with open(f, encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh)
            row = next((r for ln, r in enumerate(rd, start=2) if ln == int(c["source_line"])), None)
        rows.append((row, m))
    import numpy as np

    pts = [(float(r[0]["longitude"]), float(r[0]["latitude"])) if r else (0.0, 0.0) for r in rows]
    first, hits = bs.point_in_polygons(np.array([p[0] for p in pts]), np.array([p[1] for p in pts]), parts)
    want_coords = {}
    for e, r, fi, nh in zip(evs, rows, first, hits):
        if r is None:
            continue
        row, m = r
        region = None if fi < 0 else (feats[fi]["properties"]["KDPPUM"], feats[fi]["properties"]["WADMPR"], int(nh))
        prov = {k: e[k] for k in ce.LOAD_FIELDS}
        rebuilt = ce.build_event(e["source_id"], row, region, bs.BOUNDARY_VERSION, prov)
        diff = [k for k in ce.CONTENT_FIELDS if rebuilt[k] != e[k]]
        if diff:
            errs.append(f"{e['detection_id'][:12]}: differs from raw rebuild in {diff}")
        want_coords[(row["latitude"], row["longitude"])] = (region[0] if region else "", int(nh))
    seen = {}
    with open(data / "firms" / "profile" / "coord_assign.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            k = (r["latitude"], r["longitude"])
            if k in want_coords:
                seen[k] = (r["kdppum"], int(r["n_hits"]))
    for k, v in want_coords.items():
        if seen.get(k) != v:
            errs.append(f"region of {k} = {v}, Phase 1 coord_assign.csv = {seen.get(k)}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=pathlib.Path)
    args = ap.parse_args()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    evs = [json.loads(line) for line in SAMPLES.read_text(encoding="utf-8").splitlines() if line.strip()]
    failed = False

    def report(tag, errs, ok_msg):
        nonlocal failed
        if errs:
            failed = True
            print(f"[{tag}] FAIL ({len(errs)})")
            for x in errs:
                print("   -", x)
        else:
            print(f"[{tag}] PASS  {ok_msg}")

    s_errs = [f"line {i}: {x}" for i, e in enumerate(evs, 1) for x in schema_errors(e, schema)]
    report("schema", s_errs, f"{len(evs)}/{len(evs)} records valid against {SCHEMA.name}")
    r_errs = [f"line {i}: {x}" for i, e in enumerate(evs, 1) for x in rule_errors(e)]
    report("rules", r_errs, f"{len(evs)}/{len(evs)} records satisfy contract rules")
    c_errs, need = coverage_errors(evs)
    report("coverage", c_errs, "; ".join(need))
    t_errs, n_mut = selftest(evs, schema)
    report("selftest", t_errs, f"{n_mut} mutated records rejected; detection_id set order-independent (50 shuffles)")
    if args.data_dir:
        tr = trace_errors(evs, args.data_dir.resolve())
        report(
            "trace",
            tr,
            f"{len(evs)} records = rebuild from raw line; SHA-256 file=manifest=event; "
            "boundary checksum OK; region = Phase 1 coord_assign.csv",
        )
    else:
        print("[trace] SKIPPED (no --data-dir)")
    counts = {}
    for e in evs:
        k = (e["source_id"], e["region_status"])
        counts[k] = counts.get(k, 0) + 1
    print("mix:", ", ".join(f"{s}/{r}={n}" for (s, r), n in sorted(counts.items())))
    print("RESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
