"""Reference functions for the canonical event contract (A-P3-001, contract_version 1.0.0).

Normative text: docs/03-specs/data/02-canonical-event-contract.md. This module is the executable form of
its rules (identity, time, region, flags) so that the sample builder and the validator use one definition.
Standard library only. It is a spec artefact, not pipeline code; A-P5 may copy or import it.
"""

from __future__ import annotations

import hashlib
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

# BIG `KDPPUM` province code -> time zone (SEM-03 table, keyed by code instead of name; 18 + 12 + 8 = 38).
ZONE_OFFSET_HOURS = {"WIB": 7, "WITA": 8, "WIT": 9}
_WIB = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "31", "32", "33", "34", "35", "36", "61", "62"]
_WITA = ["51", "52", "53", "63", "64", "65", "71", "72", "73", "74", "75", "76"]
_WIT = ["81", "82", "91", "92", "93", "94", "95", "96"]
PROVINCE_ZONE = {**{c: "WIB" for c in _WIB}, **{c: "WITA" for c in _WITA}, **{c: "WIT" for c in _WIT}}
assert len(PROVINCE_ZONE) == 38

CONFIDENCE_CLASS = {"l": "low", "n": "nominal", "h": "high"}
TI4_SATURATION_K = 367.0  # DQ-09
DQ_FLAGS = ("FRP_ZERO", "MULTI_POLYGON", "NON_VEGETATION_TYPE", "TI4_SATURATED")

# Fields that describe the detection itself (row-intrinsic + boundary). Load-provenance fields are excluded:
# they may legitimately differ between two loads of the same detection (contract §6).
CONTENT_FIELDS = (
    "detection_id",
    "source_id",
    "processing_level",
    "version_raw",
    "satellite",
    "instrument",
    "acq_datetime_utc",
    "source_acq_date_utc",
    "local_date",
    "local_tz",
    "latitude",
    "longitude",
    "region_status",
    "province_code",
    "province_name",
    "boundary_version",
    "bright_ti4",
    "bright_ti5",
    "scan",
    "track",
    "frp",
    "confidence_raw",
    "confidence_class",
    "daynight",
    "type",
    "dq_flags",
)
LOAD_FIELDS = ("source_file", "source_file_sha256", "fetched_at_utc", "ingest_run_id")


def canonical_decimal(text: str) -> str:
    """Source coordinate text -> canonical decimal string (no exponent, no trailing zeros, no '-0')."""
    d = Decimal(text.strip()).normalize()
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def acq_datetime_utc(acq_date: str, acq_time: str) -> datetime:
    """`acq_date` (UTC, YYYY-MM-DD) + `acq_time` (HHMM, leading zeros dropped by FIRMS) -> aware UTC datetime."""
    hhmm = acq_time.strip().zfill(4)
    if len(hhmm) != 4 or not hhmm.isdigit():
        raise ValueError(f"INVALID_TIME: {acq_time!r}")
    hh, mm = int(hhmm[:2]), int(hhmm[2:])
    if hh > 23 or mm > 59:
        raise ValueError(f"INVALID_TIME: {acq_time!r}")
    d = date.fromisoformat(acq_date.strip())
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=UTC)


def format_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def detection_id(processing_level: str, satellite: str, dt_utc: datetime, lat_text: str, lon_text: str) -> str:
    """Deterministic identity (contract §4): SHA-256 hex of the canonical identity string."""
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


def build_event(
    source_id: str, row: dict, region: tuple[str, str, int] | None, boundary_version: str, provenance: dict
) -> dict:
    """One raw FIRMS row (dict of source column -> text) -> canonical event.

    region: (province_code, province_name, n_polygon_hits) or None when the point is in no polygon (OUTSIDE).
    provenance: source_file, source_file_sha256, fetched_at_utc, ingest_run_id.
    Raw-row rejection (DQ-01..06, 13..15) is the pipeline's job and is not repeated here beyond parsing.
    """
    satellite, level, version = SOURCES[source_id]
    if row["satellite"] != satellite:
        raise ValueError("SATELLITE_MISMATCH")
    if row["version"] != version:
        raise ValueError("VERSION_MISMATCH")
    dt = acq_datetime_utc(row["acq_date"], row["acq_time"])
    type_raw = row.get("type")
    type_ = None if level == "NRT" or type_raw in (None, "") else int(type_raw)
    ti4, frp = float(row["bright_ti4"]), float(row["frp"])
    if region is None:
        status, code, name, zone, ldate, hits = "OUTSIDE", None, None, None, None, 0
    else:
        code, name, hits = region
        status, zone = "INSIDE", PROVINCE_ZONE[code]
        ldate = local_date(dt, zone)
    return {
        "detection_id": detection_id(level, satellite, dt, row["latitude"], row["longitude"]),
        "source_id": source_id,
        "processing_level": level,
        "version_raw": row["version"],
        "satellite": satellite,
        "instrument": row["instrument"],
        "acq_datetime_utc": format_utc(dt),
        "source_acq_date_utc": row["acq_date"],
        "local_date": ldate,
        "local_tz": zone,
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "region_status": status,
        "province_code": code,
        "province_name": name,
        "boundary_version": boundary_version,
        "bright_ti4": ti4,
        "bright_ti5": float(row["bright_ti5"]),
        "scan": float(row["scan"]),
        "track": float(row["track"]),
        "frp": frp,
        "confidence_raw": row["confidence"],
        "confidence_class": CONFIDENCE_CLASS[row["confidence"]],
        "daynight": row["daynight"],
        "type": type_,
        "dq_flags": dq_flags(ti4, frp, type_, hits),
        "source_file": provenance["source_file"],
        "source_file_sha256": provenance["source_file_sha256"],
        "fetched_at_utc": provenance["fetched_at_utc"],
        "ingest_run_id": provenance["ingest_run_id"],
    }
