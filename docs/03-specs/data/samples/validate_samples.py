"""Validate canonical-events.sample.jsonl (A-P3-001).

Checks, in order:
  [schema]   every record against canonical-event.schema.json (JSON Schema 2020-12 subset, stdlib only;
             unknown keywords are an error, so nothing is silently skipped)
  [rules]    contract rules a schema cannot express (detection_id, local date, zone, flags, source mapping, uniqueness)
  [coverage] the sample mix required by 06-interface-contracts §B and the A-P3-001 task card
  [selftest] mutated records must be rejected (negative tests) + order-independence of detection_id
  [edge]     unit edge cases of the reference functions on synthetic input (time padding, date rollover at
             zone boundaries / year end / leap day, coordinate text forms, strict number parsing, reason codes,
             identity separation SP/NRT and N20/N21); every synthetic event that is built must pass [schema]+[rules]
  [trace]    (only with --data-dir) each record equals a rebuild from its raw CSV line; file SHA-256 = manifest =
             actual file; boundary snapshot checksum; region agrees with Phase 1 coord_assign.csv

Usage:
    python -I docs/03-specs/data/samples/validate_samples.py [--data-dir D:/Kuliah/apiwowok/data]
Exit 0 = all checks passed. Full raw-zone audit (all rows): audit_raw_zone.py.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import pathlib
import random
import re
import sys
from datetime import date, datetime

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import canonical_event as ce

SAMPLES = HERE / "canonical-events.sample.jsonl"
CASES = HERE / "canonical-events.sample.cases.csv"
SCHEMA = HERE / "canonical-event.schema.json"
NUMERIC_FIELDS = ("latitude", "longitude", "bright_ti4", "bright_ti5", "scan", "track", "frp")


def _reject_constant(name):
    raise ValueError(f"non-standard JSON constant {name} (NaN/Infinity are not valid JSON)")


def load_jsonl(text: str) -> list[dict]:
    """Strict JSONL: Python's json accepts NaN/Infinity by default; the contract does not."""
    return [json.loads(line, parse_constant=_reject_constant) for line in text.splitlines() if line.strip()]


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
    bad_num = [k for k in NUMERIC_FIELDS if not (_TYPES["number"](e.get(k)) and math.isfinite(e[k]))]
    if bad_num:
        return [f"non-finite or non-numeric value in {bad_num}"]
    for d in ("source_acq_date_utc", "local_date"):
        if isinstance(e.get(d), str):
            try:
                date.fromisoformat(e[d])
            except ValueError:
                errs.append(f"{d} is not a real calendar date: {e[d]!r}")
    if e.get("province_code") in ce.PROVINCE_NAME and e.get("province_name") != ce.PROVINCE_NAME[e["province_code"]]:
        errs.append(f"province_name {e.get('province_name')!r} != BIG name of {e['province_code']}")
    if ".." in str(e.get("source_file", "")).split("/"):
        errs.append("source_file contains a '..' segment")
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
    sp_file_for_nrt = base_inside["source_file"].replace("_NRT/", "_SP/")
    mutations = {
        "NRT dengan type 0": (base_inside, {"type": 0}),
        "SP dengan type 4": (base_sp, {"type": 4}),
        "province_name tidak cocok kode": (base_inside, {"province_name": "Bali"}),
        "frp NaN": (base_inside, {"frp": float("nan")}),
        "latitude Infinity": (base_inside, {"latitude": float("inf")}),
        "latitude di luar ±90": (base_inside, {"latitude": 91.0}),
        "bright_ti4 = 0": (base_inside, {"bright_ti4": 0.0}),
        "frp negatif": (base_inside, {"frp": -1.0}),
        "daynight X": (base_inside, {"daynight": "X"}),
        "source_file dengan '..'": (base_inside, {"source_file": base_inside["source_id"] + "/../x.csv"}),
        "source_file produk lain (SP untuk event NRT)": (base_inside, {"source_file": sp_file_for_nrt}),
        "local_date bukan tanggal nyata": (base_inside, {"local_date": "2026-02-30"}),
        "source_acq_date_utc bukan tanggal nyata": (base_inside, {"source_acq_date_utc": "2026-13-01"}),
        "jam 24:00": (base_inside, {"acq_datetime_utc": base_inside["acq_datetime_utc"][:11] + "24:00:00Z"}),
        "detik bukan 00": (base_inside, {"acq_datetime_utc": base_inside["acq_datetime_utc"][:17] + "30Z"}),
        "dq_flags duplikat": (base_sp, {"dq_flags": ["FRP_ZERO", "FRP_ZERO"]}),
        "region_status tidak dikenal": (base_inside, {"region_status": "PROVINCE"}),
        "province_code bukan 38 kode": (base_inside, {"province_code": "99"}),
        "type boolean": (base_sp, {"type": False}),
        "latitude string": (base_inside, {"latitude": "1.5"}),
        "ingest_run_id kosong": (base_inside, {"ingest_run_id": ""}),
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
    # Positive mutation: CE-09 (SP row with empty `type`) must be ACCEPTED.
    sp_null = copy.deepcopy(base_sp)
    sp_null["type"] = None
    sp_null["dq_flags"] = [f for f in sp_null["dq_flags"] if f != "NON_VEGETATION_TYPE"]
    if schema_errors(sp_null, schema) or _safe_rules(sp_null):
        errs.append("CE-09: SP event with type null was rejected (should be accepted)")
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


# ---------------------------------------------------------------- unit edge cases (synthetic input)
_PROV = {
    "source_file": "VIIRS_NOAA20_SP/edge.csv",
    "source_file_sha256": "0" * 64,
    "fetched_at_utc": "2026-11-19T09:00:34Z",
    "ingest_run_id": "edge",
}
_BV = "BIG-2026-06-g0.001-0382eeeeb559"


def _row(**kw) -> dict:
    r = {
        "latitude": "-2.88674", "longitude": "116.2264", "bright_ti4": "327.42", "scan": "0.34", "track": "0.56",
        "acq_date": "2023-01-01", "acq_time": "508", "satellite": "N20", "instrument": "VIIRS", "confidence": "n",
        "version": "2", "bright_ti5": "271.36", "frp": "1.66", "daynight": "D", "type": "0",
    }  # fmt: skip
    r.update(kw)
    return {k: v for k, v in r.items() if v is not None}


def _nrt_row(**kw) -> dict:
    r = _row(version="2.0NRT", **kw)
    r.pop("type", None)
    return r


def edge_errors(schema: dict) -> tuple[list[str], int]:
    errs, n = [], 0

    def check(name, cond):
        nonlocal n
        n += 1
        if callable(cond):  # evaluated here so an unexpected exception is a failed case, not a crash
            try:
                cond = cond()
            except (ArithmeticError, KeyError, TypeError, ValueError) as x:
                errs.append(f"{name} (raised {x!r})")
                return
        if not cond:
            errs.append(name)

    def rejected(fn, code):
        try:
            fn()
        except ce.RowRejected as x:
            return x.code == code
        except (ArithmeticError, KeyError, TypeError, ValueError):
            return False  # wrong exception type = no reason code = test fails (reported, not a crash)
        return False

    def built_ok(e):
        return not schema_errors(e, schema) and not rule_errors(e)

    utc = lambda d, t: ce.acq_datetime_utc(d, t)
    # acq_time padding and range (DQ-05)
    for t, hm in [("0", "00:00"), ("5", "00:05"), ("59", "00:59"), ("100", "01:00"), ("508", "05:08"),
                  ("2359", "23:59"), (" 508 ", "05:08")]:  # fmt: skip
        check(f"acq_time {t!r} -> {hm}", utc("2023-01-01", t).strftime("%H:%M") == hm)
    for t in ["2400", "1260", "12345", "-5", "5.0", "+508", "٥٠٨", "5 08", "0x1f"]:
        check(f"acq_time {t!r} rejected INVALID_TIME", rejected(lambda t=t: utc("2023-01-01", t), "INVALID_TIME"))
    check("acq_time '' -> MISSING_FIELD", rejected(lambda: utc("2023-01-01", ""), "MISSING_FIELD"))
    # acq_date
    check("2024-02-29 valid", utc("2024-02-29", "1200").date() == date(2024, 2, 29))
    for d in ["2023-02-29", "2023-1-1", "2023/01/01", "20230101", "2023-01-01T00:00"]:
        check(f"acq_date {d!r} rejected", rejected(lambda d=d: utc(d, "1200"), "CONTRACT_VIOLATION"))
    # local date rollover at zone thresholds, year end, leap day
    cases = [
        ("2023-12-31", "1659", "WIB", "2023-12-31"), ("2023-12-31", "1700", "WIB", "2024-01-01"),
        ("2023-12-31", "1559", "WITA", "2023-12-31"), ("2023-12-31", "1600", "WITA", "2024-01-01"),
        ("2023-12-31", "1459", "WIT", "2023-12-31"), ("2023-12-31", "1500", "WIT", "2024-01-01"),
        ("2024-02-28", "1730", "WIB", "2024-02-29"), ("2024-02-29", "1500", "WIT", "2024-03-01"),
        ("2023-02-28", "1700", "WIB", "2023-03-01"), ("2023-01-01", "0000", "WIT", "2023-01-01"),
        ("2023-01-01", "2359", "WIB", "2023-01-02"),
    ]  # fmt: skip
    for d, t, z, want in cases:
        check(f"local_date {d} {t} {z} -> {want}", ce.local_date(utc(d, t), z) == want)
    # coordinate text canonicalisation (identity input)
    same = [("-1.50000", "-1.5"), ("116.22640", "116.2264"), ("100.0", "100"), ("-0.000", "0"), ("0", "0"),
            ("-0", "0"), ("007.5", "7.5"), ("0.00001", "0.00001"), ("-11.5", "-11.5"),
            ("-7e-05", "-0.00007"), ("1e-05", "0.00001"), ("1E-5", "0.00001"), ("9e-05", "0.00009"),
            ("1.5e+1", "15"), ("-0e-05", "0")]  # fmt: skip
    for a, b in same:
        check(f"canon({a!r}) == {b!r}", lambda a=a, b=b: ce.canonical_decimal(a) == b)
    for bad in [
        "nan",
        "NaN",
        "inf",
        "-Infinity",
        "+1.5",
        "1_000",
        "1.",
        ".5",
        "1,5",
        "",
        " ",
        "--1",
        "1e",
        "e5",
        "1e-",
        "1e5.5",
        "0x10",
    ]:
        code = "MISSING_FIELD" if bad.strip() == "" else "NON_NUMERIC"
        check(f"canon({bad!r}) rejected {code}", rejected(lambda b=bad: ce.canonical_decimal(b), code))
    # identity separation and stability
    dt = utc("2023-01-01", "508")
    base = ce.detection_id("SP", "N20", dt, "-2.88674", "116.2264")
    check("id: example from contract §4", base == "91ff7b55df045269b4915214e53dea278a1b6e6237a1958e7ebe663126df3d45")
    check("id: SP != NRT (CR-03)", base != ce.detection_id("NRT", "N20", dt, "-2.88674", "116.2264"))
    check("id: N20 != N21", base != ce.detection_id("SP", "N21", dt, "-2.88674", "116.2264"))
    check(
        "id: +1 minute differs", base != ce.detection_id("SP", "N20", utc("2023-01-01", "509"), "-2.88674", "116.2264")
    )
    check("id: lat/lon swapped differs", base != ce.detection_id("SP", "N20", dt, "116.2264", "-2.88674"))
    check("id: trailing zeros same", base == ce.detection_id("SP", "N20", dt, "-2.886740", "116.22640"))
    check("id: 5th decimal differs", base != ce.detection_id("SP", "N20", dt, "-2.88675", "116.2264"))
    near_eq = lambda lat: ce.detection_id("NRT", "N20", dt, lat, "101.5")
    check("id: exponent == decimal form (FIRMS near-equator)", lambda: near_eq("-7e-05") == near_eq("-0.00007"))
    check("id: -7e-05 != 7e-05", lambda: near_eq("-7e-05") != near_eq("7e-05"))
    # timestamps
    check("ts +00:00 -> Z", ce.normalize_utc_timestamp("2026-11-19T09:00:34+00:00") == "2026-11-19T09:00:34Z")
    check("ts +07:00 -> UTC", ce.normalize_utc_timestamp("2026-11-19T16:00:34+07:00") == "2026-11-19T09:00:34Z")
    check("ts fraction dropped", ce.normalize_utc_timestamp("2026-11-19T09:00:34.987Z") == "2026-11-19T09:00:34Z")
    check(
        "ts naive rejected", rejected(lambda: ce.normalize_utc_timestamp("2026-11-19T09:00:34"), "CONTRACT_VIOLATION")
    )
    # build_event: reason codes and flags on synthetic rows
    sp, nrt = "VIIRS_NOAA20_SP", "VIIRS_NOAA20_NRT"
    nrt_prov = dict(_PROV, source_file="VIIRS_NOAA20_NRT/edge.csv")
    inside = ("63", "Kalimantan Selatan", 1)
    be = lambda src, row, region=inside, prov=_PROV: ce.build_event(src, row, region, _BV, prov)

    def sb(*a, **k):  # build that must succeed; a rejection is reported as a failed case, not a crash
        try:
            return be(*a, **k)
        except (ArithmeticError, KeyError, TypeError, ValueError):
            return None

    rej = {
        "SP version 2.0NRT -> VERSION_MISMATCH": (sp, _row(version="2.0NRT"), "VERSION_MISMATCH"),
        "SP version '2.0' -> VERSION_MISMATCH": (sp, _row(version="2.0"), "VERSION_MISMATCH"),
        "satellite N21 in NOAA20 -> SATELLITE_MISMATCH": (sp, _row(satellite="N21"), "SATELLITE_MISMATCH"),
        "confidence 'N' -> INVALID_CONFIDENCE": (sp, _row(confidence="N"), "INVALID_CONFIDENCE"),
        "confidence '' -> MISSING_FIELD": (sp, _row(confidence=""), "MISSING_FIELD"),
        "frp '' -> MISSING_FIELD": (sp, _row(frp=""), "MISSING_FIELD"),
        "frp 'NaN' -> NON_NUMERIC": (sp, _row(frp="NaN"), "NON_NUMERIC"),
        "bright_ti4 'abc' -> NON_NUMERIC": (sp, _row(bright_ti4="abc"), "NON_NUMERIC"),
        "latitude '95' -> COORD_OUT_OF_RANGE": (sp, _row(latitude="95"), "COORD_OUT_OF_RANGE"),
        "latitude '1e400' (overflow) -> COORD_OUT_OF_RANGE": (sp, _row(latitude="1e400"), "COORD_OUT_OF_RANGE"),
        "frp '1e400' (overflow) -> NON_NUMERIC": (sp, _row(frp="1e400"), "NON_NUMERIC"),
        "frp '-1' -> CONTRACT_VIOLATION": (sp, _row(frp="-1"), "CONTRACT_VIOLATION"),
        "scan '0' -> CONTRACT_VIOLATION": (sp, _row(scan="0"), "CONTRACT_VIOLATION"),
        "type '4' -> CONTRACT_VIOLATION": (sp, _row(type="4"), "CONTRACT_VIOLATION"),
        "type '1.0' -> NON_NUMERIC": (sp, _row(type="1.0"), "NON_NUMERIC"),
        "daynight 'X' -> CONTRACT_VIOLATION": (sp, _row(daynight="X"), "CONTRACT_VIOLATION"),
        "instrument 'MODIS' -> CONTRACT_VIOLATION": (sp, _row(instrument="MODIS"), "CONTRACT_VIOLATION"),
        "NRT row with type column -> SCHEMA_MISMATCH": (nrt, dict(_nrt_row(), type="0"), "SCHEMA_MISMATCH"),
        "unknown source_id -> CONTRACT_VIOLATION": ("VIIRS_SNPP_SP", _row(), "CONTRACT_VIOLATION"),
    }
    for name, (src, row, code) in rej.items():
        prov = nrt_prov if src == nrt else _PROV
        check(name, rejected(lambda src=src, row=row, prov=prov: be(src, row, prov=prov), code))
    check(
        "unknown province code -> CONTRACT_VIOLATION",
        rejected(lambda: be(sp, _row(), ("99", "X", 1)), "CONTRACT_VIOLATION"),
    )
    check(
        "province name not BIG -> CONTRACT_VIOLATION",
        rejected(lambda: be(sp, _row(), ("31", "DKI Jakarta", 1)), "CONTRACT_VIOLATION"),
    )
    ok = {
        "SP baseline": (sb(sp, _row()), {"type": 0, "dq_flags": [], "local_date": "2023-01-01"}),
        "CE-09: SP empty type -> null": (sb(sp, _row(type="")), {"type": None}),
        "SP type missing column -> null": (sb(sp, _row(type=None)), {"type": None}),
        "NRT -> type null": (sb(nrt, _nrt_row(), prov=nrt_prov), {"type": None, "processing_level": "NRT"}),
        "frp '0' -> FRP_ZERO": (sb(sp, _row(frp="0")), {"dq_flags": ["FRP_ZERO"]}),
        "frp '0.00' -> FRP_ZERO": (sb(sp, _row(frp="0.00")), {"dq_flags": ["FRP_ZERO"]}),
        "ti4 '367' -> TI4_SATURATED": (sb(sp, _row(bright_ti4="367")), {"dq_flags": ["TI4_SATURATED"]}),
        "ti4 '367.00' -> TI4_SATURATED": (sb(sp, _row(bright_ti4="367.00")), {"dq_flags": ["TI4_SATURATED"]}),
        "ti4 '366.99' -> no flag": (sb(sp, _row(bright_ti4="366.99")), {"dq_flags": []}),
        "type 3 -> NON_VEGETATION_TYPE": (sb(sp, _row(type="3")), {"dq_flags": ["NON_VEGETATION_TYPE"]}),
        "2 polygons -> MULTI_POLYGON": (
            sb(sp, _row(), ("63", "Kalimantan Selatan", 2)),
            {"dq_flags": ["MULTI_POLYGON"]},
        ),
        "all flags sorted": (
            sb(sp, _row(frp="0", bright_ti4="367", type="2"), ("63", "Kalimantan Selatan", 3)),
            {"dq_flags": ["FRP_ZERO", "MULTI_POLYGON", "NON_VEGETATION_TYPE", "TI4_SATURATED"]},
        ),
        "OUTSIDE -> nulls": (
            sb(sp, _row(), None),
            {"region_status": "OUTSIDE", "province_code": None, "local_date": None, "local_tz": None},
        ),
        "OUTSIDE ignores polygon hits": (sb(sp, _row(), None), {"dq_flags": []}),
        "night rollover WIT": (
            sb(sp, _row(acq_time="1500", daynight="N"), ("91", "Papua", 1)),
            {"local_date": "2023-01-02", "source_acq_date_utc": "2023-01-01"},
        ),
        "whitespace in date trimmed": (sb(sp, _row(acq_date=" 2023-01-01 ")), {"source_acq_date_utc": "2023-01-01"}),
        "jakarta BIG name": (sb(sp, _row(), ("31", "Daerah Khusus Ibukota Jakarta", 1)), {"local_tz": "WIB"}),
        "latitude '-7e-05' accepted": (sb(sp, _row(latitude="-7e-05")), {"latitude": -7e-05}),
    }
    for name, (e, want) in ok.items():
        check(f"{name}: built without rejection", e is not None)
        if e is not None:
            check(f"{name}: values", all(e[k] == v for k, v in want.items()))
            check(f"{name}: passes schema+rules", built_ok(e))
    check("JSON NaN literal rejected by loader", rejected_json('{"frp": NaN}'))
    check("JSON Infinity literal rejected by loader", rejected_json('{"frp": Infinity}'))
    return errs, n


def rejected_json(text: str) -> bool:
    try:
        load_jsonl(text)
    except ValueError:
        return True
    return False


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
        if ce.normalize_utc_timestamp(m["fetched_at_utc"]) != e["fetched_at_utc"]:
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
    evs = load_jsonl(SAMPLES.read_text(encoding="utf-8"))
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
    report(
        "selftest",
        t_errs,
        f"{n_mut} mutated records rejected; CE-09 SP type null accepted; detection_id set order-independent (50 shuffles)",
    )
    e_errs, n_edge = edge_errors(schema)
    report("edge", [f"edge case failed: {x}" for x in e_errs], f"{n_edge}/{n_edge} unit edge cases")
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
