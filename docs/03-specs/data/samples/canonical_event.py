"""Reference functions for the canonical event contract (A-P3-001, contract_version 1.0.0).

Normative text: docs/03-specs/data/02-canonical-event-contract.md. This module is the executable form of
its rules (identity, time, region, flags, parsing) so that the sample builder, the validator and the raw-zone
audit use one definition. Standard library only; Python >= 3.11 (datetime.UTC). It is a spec artefact, not
pipeline code; A-P5 may copy or import it.

Every failure raises RowRejected with a reason code: the DQ code from 06-data-quality-rules.md when one
applies, otherwise CONTRACT_VIOLATION (CE-08).
"""

from __future__ import annotations

import hashlib
import math
import re
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

CONTRACT_VERSION = "1.0.0"

# Source ID (request metadata) -> (satellite, processing_level, expected `version` value). DQ-14, DQ-15.
SOURCES = {
    "VIIRS_NOAA20_SP": ("N20", "SP", "2"),
    "VIIRS_NOAA21_SP": ("N21", "SP", "2"),
    "VIIRS_NOAA20_NRT": ("N20", "NRT", "2.0NRT"),
    "VIIRS_NOAA21_NRT": ("N21", "NRT", "2.0NRT"),
}

# BIG `KDPPUM` -> `WADMPR` (snapshot big_kabkota_2026_06_off0.001, verified 2026-11-26) and time zone
# (SEM-03 table, keyed by code instead of name; 18 + 12 + 8 = 38).
PROVINCE_NAME = {
    "11": "Aceh", "12": "Sumatera Utara", "13": "Sumatera Barat", "14": "Riau", "15": "Jambi",
    "16": "Sumatera Selatan", "17": "Bengkulu", "18": "Lampung", "19": "Kepulauan Bangka Belitung",
    "21": "Kepulauan Riau", "31": "Daerah Khusus Ibukota Jakarta", "32": "Jawa Barat", "33": "Jawa Tengah",
    "34": "Daerah Istimewa Yogyakarta", "35": "Jawa Timur", "36": "Banten", "51": "Bali",
    "52": "Nusa Tenggara Barat", "53": "Nusa Tenggara Timur", "61": "Kalimantan Barat",
    "62": "Kalimantan Tengah", "63": "Kalimantan Selatan", "64": "Kalimantan Timur", "65": "Kalimantan Utara",
    "71": "Sulawesi Utara", "72": "Sulawesi Tengah", "73": "Sulawesi Selatan", "74": "Sulawesi Tenggara",
    "75": "Gorontalo", "76": "Sulawesi Barat", "81": "Maluku", "82": "Maluku Utara", "91": "Papua",
    "92": "Papua Barat", "93": "Papua Selatan", "94": "Papua Tengah", "95": "Papua Pegunungan",
    "96": "Papua Barat Daya",
}  # fmt: skip
ZONE_OFFSET_HOURS = {"WIB": 7, "WITA": 8, "WIT": 9}
_WIB = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "31", "32", "33", "34", "35", "36", "61", "62"]
_WITA = ["51", "52", "53", "63", "64", "65", "71", "72", "73", "74", "75", "76"]
_WIT = ["81", "82", "91", "92", "93", "94", "95", "96"]
PROVINCE_ZONE = {**{c: "WIB" for c in _WIB}, **{c: "WITA" for c in _WITA}, **{c: "WIT" for c in _WIT}}
assert len(PROVINCE_ZONE) == 38 and PROVINCE_ZONE.keys() == PROVINCE_NAME.keys()

CONFIDENCE_CLASS = {"l": "low", "n": "nominal", "h": "high"}
TI4_SATURATION_K = 367.0  # DQ-09
DQ_FLAGS = ("FRP_ZERO", "MULTI_POLYGON", "NON_VEGETATION_TYPE", "TI4_SATURATED")

# Fields that describe the detection itself (row-intrinsic + boundary). Load-provenance fields are excluded:
# they may legitimately differ between two loads of the same detection (contract §8, CE-04).
CONTENT_FIELDS = (
    "detection_id", "source_id", "processing_level", "version_raw", "satellite", "instrument",
    "acq_datetime_utc", "source_acq_date_utc", "local_date", "local_tz", "latitude", "longitude",
    "region_status", "province_code", "province_name", "boundary_version", "bright_ti4", "bright_ti5",
    "scan", "track", "frp", "confidence_raw", "confidence_class", "daynight", "type", "dq_flags",
)  # fmt: skip
LOAD_FIELDS = ("source_file", "source_file_sha256", "fetched_at_utc", "ingest_run_id")

# Number as FIRMS writes it: optional '-', ASCII digits, optional fraction, optional exponent. The exponent is
# real: FIRMS writes latitudes within 1e-4 of the equator as e.g. '-7e-05' (22 of 2,705,905 Phase 1 rows,
# audit_raw_zone.py). Rejected: '+', underscore, inner whitespace, '1.', '.5', NaN, Infinity (Python's
# float()/Decimal() would accept several of these).
_DECIMAL = re.compile(r"-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?")
_HHMM = re.compile(r"[0-9]{1,4}")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class RowRejected(ValueError):
    """A raw row (or file) that cannot become a canonical event. `code` = reason code for the run log."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _decimal_text(text: str | None, field: str) -> str:
    if text is None or text.strip() == "":
        raise RowRejected("MISSING_FIELD", field)  # DQ-02
    t = text.strip()
    if not _DECIMAL.fullmatch(t):
        raise RowRejected("NON_NUMERIC", f"{field}={text!r}")  # DQ-03
    return t


def parse_number(text: str | None, field: str) -> float:
    v = float(_decimal_text(text, field))
    if not math.isfinite(v):  # cannot happen after the regex; kept as a guard
        raise RowRejected("NON_NUMERIC", f"{field}={text!r}")
    return v


def canonical_decimal(text: str) -> str:
    """Source coordinate text -> canonical decimal string (no exponent, no trailing zeros, no trailing '.', no '-0').

    '-7e-05', '-0.00007' and '-0.000070' all give '-0.00007', so the identity does not depend on how FIRMS
    happened to format the number.
    """
    d = Decimal(_decimal_text(text, "coordinate"))
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def acq_datetime_utc(acq_date: str, acq_time: str) -> datetime:
    """`acq_date` (UTC, YYYY-MM-DD) + `acq_time` (HHMM, leading zeros dropped by FIRMS) -> aware UTC datetime."""
    t = (acq_time or "").strip()
    if t == "":
        raise RowRejected("MISSING_FIELD", "acq_time")
    if not _HHMM.fullmatch(t):
        raise RowRejected("INVALID_TIME", repr(acq_time))  # DQ-05
    hh, mm = int(t.zfill(4)[:2]), int(t.zfill(4)[2:])
    if hh > 23 or mm > 59:
        raise RowRejected("INVALID_TIME", repr(acq_time))
    ds = (acq_date or "").strip()
    if ds == "":
        raise RowRejected("MISSING_FIELD", "acq_date")
    try:
        if not _ISO_DATE.fullmatch(ds):
            raise ValueError
        d = date.fromisoformat(ds)
    except ValueError:
        raise RowRejected("CONTRACT_VIOLATION", f"acq_date={acq_date!r}") from None
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=UTC)


def format_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_utc_timestamp(text: str) -> str:
    """ISO-8601 timestamp WITH offset (e.g. manifest '2026-11-19T09:00:34+00:00') -> 'YYYY-MM-DDTHH:MM:SSZ'."""
    dt = datetime.fromisoformat(text.strip())  # Python >= 3.11 accepts a trailing Z
    if dt.tzinfo is None:
        raise RowRejected("CONTRACT_VIOLATION", f"timestamp without offset: {text!r}")
    return format_utc(dt.replace(microsecond=0))


def detection_id(processing_level: str, satellite: str, dt_utc: datetime, lat_text: str, lon_text: str) -> str:
    """Deterministic identity (contract §4, CE-01): SHA-256 hex of the canonical identity string."""
    key = "|".join(
        [
            processing_level,
            satellite,
            dt_utc.astimezone(UTC).strftime("%Y-%m-%dT%H:%MZ"),
            canonical_decimal(lat_text),
            canonical_decimal(lon_text),
        ]
    )
    return hashlib.sha256(key.encode("ascii")).hexdigest()


def local_date(dt_utc: datetime, zone: str) -> str:
    return (dt_utc + timedelta(hours=ZONE_OFFSET_HOURS[zone])).date().isoformat()


def dq_flags(bright_ti4: float, frp: float, type_: int | None, n_polygon_hits: int) -> list[str]:
    flags = set()
    if bright_ti4 == TI4_SATURATION_K:
        flags.add("TI4_SATURATED")
    if frp == 0.0:
        flags.add("FRP_ZERO")
    if type_ in (1, 2, 3):
        flags.add("NON_VEGETATION_TYPE")
    if n_polygon_hits > 1:
        flags.add("MULTI_POLYGON")
    return sorted(flags)


def _parse_type(level: str, row: dict) -> int | None:
    if level == "NRT":
        if "type" in row:  # NRT header has 14 columns; a `type` column means DQ-01 should have rejected the file
            raise RowRejected("SCHEMA_MISMATCH", "NRT row with a type column")
        return None
    raw = (row.get("type") or "").strip()
    if raw == "":
        return None  # CE-09: DQ-02 exempts `type`; an empty SP type is accepted as unknown (null)
    if not re.fullmatch(r"[0-9]+", raw):
        raise RowRejected("NON_NUMERIC", f"type={raw!r}")
    v = int(raw)
    if v not in (0, 1, 2, 3):
        raise RowRejected("CONTRACT_VIOLATION", f"type={v}")  # CE-08
    return v


def build_event(
    source_id: str, row: dict, region: tuple[str, str, int] | None, boundary_version: str, provenance: dict
) -> dict:
    """One raw FIRMS row (dict of source column -> text) -> canonical event, or RowRejected.

    region: (province_code, province_name, n_polygon_hits) or None when the point is in no polygon (OUTSIDE).
    provenance: source_file, source_file_sha256, fetched_at_utc, ingest_run_id.
    File-level DQ (DQ-01 header, DQ-14/15 per file) and window/bbox checks (DQ-04 bbox, DQ-06) need request
    metadata and stay in the pipeline; the per-row form of DQ-14/15 and the value checks are repeated here.
    """
    if source_id not in SOURCES:
        raise RowRejected("CONTRACT_VIOLATION", f"source_id={source_id!r}")
    satellite, level, version = SOURCES[source_id]
    if (row.get("satellite") or "").strip() != satellite:
        raise RowRejected("SATELLITE_MISMATCH", repr(row.get("satellite")))  # DQ-15
    if (row.get("version") or "").strip() != version:
        raise RowRejected("VERSION_MISMATCH", repr(row.get("version")))  # DQ-14
    dt = acq_datetime_utc(row.get("acq_date"), row.get("acq_time"))
    lat_t, lon_t = _decimal_text(row.get("latitude"), "latitude"), _decimal_text(row.get("longitude"), "longitude")
    lat, lon = float(lat_t), float(lon_t)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise RowRejected("COORD_OUT_OF_RANGE", f"{lat_t},{lon_t}")  # DQ-04 (global part)
    num = {k: parse_number(row.get(k), k) for k in ("bright_ti4", "bright_ti5", "scan", "track", "frp")}
    if min(num["bright_ti4"], num["bright_ti5"], num["scan"], num["track"]) <= 0 or num["frp"] < 0:
        raise RowRejected("CONTRACT_VIOLATION", f"non-positive measurement {num}")  # CE-08
    conf = (row.get("confidence") or "").strip()
    if conf == "":
        raise RowRejected("MISSING_FIELD", "confidence")
    if conf not in CONFIDENCE_CLASS:
        raise RowRejected("INVALID_CONFIDENCE", repr(conf))  # DQ-13
    daynight = (row.get("daynight") or "").strip()
    if daynight not in ("D", "N"):
        raise RowRejected("MISSING_FIELD" if daynight == "" else "CONTRACT_VIOLATION", f"daynight={daynight!r}")
    instrument = (row.get("instrument") or "").strip()
    if instrument != "VIIRS":
        raise RowRejected("MISSING_FIELD" if instrument == "" else "CONTRACT_VIOLATION", f"instrument={instrument!r}")
    type_ = _parse_type(level, row)
    if region is None:
        status, code, name, zone, ldate, hits = "OUTSIDE", None, None, None, None, 0
    else:
        code, name, hits = region
        if code not in PROVINCE_ZONE or name != PROVINCE_NAME[code]:
            raise RowRejected("CONTRACT_VIOLATION", f"unknown province {code!r} {name!r} (boundary/table mismatch)")
        status, zone = "INSIDE", PROVINCE_ZONE[code]
        ldate = local_date(dt, zone)
    return {
        "detection_id": detection_id(level, satellite, dt, lat_t, lon_t),
        "source_id": source_id,
        "processing_level": level,
        "version_raw": version,
        "satellite": satellite,
        "instrument": instrument,
        "acq_datetime_utc": format_utc(dt),
        "source_acq_date_utc": dt.date().isoformat(),
        "local_date": ldate,
        "local_tz": zone,
        "latitude": lat,
        "longitude": lon,
        "region_status": status,
        "province_code": code,
        "province_name": name,
        "boundary_version": boundary_version,
        "bright_ti4": num["bright_ti4"],
        "bright_ti5": num["bright_ti5"],
        "scan": num["scan"],
        "track": num["track"],
        "frp": num["frp"],
        "confidence_raw": conf,
        "confidence_class": CONFIDENCE_CLASS[conf],
        "daynight": daynight,
        "type": type_,
        "dq_flags": dq_flags(num["bright_ti4"], num["frp"], type_, hits),
        "source_file": provenance["source_file"],
        "source_file_sha256": provenance["source_file_sha256"],
        "fetched_at_utc": provenance["fetched_at_utc"],
        "ingest_run_id": provenance["ingest_run_id"],
    }
