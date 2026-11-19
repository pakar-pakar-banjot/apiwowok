"""Shared helpers for one-off Phase 1 scripts. Never prints the MAP_KEY."""
import os, re, pathlib
REPO = pathlib.Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "firms"
BASE = "https://firms.modaps.eosdis.nasa.gov"
# Indonesia bounding box with margin (W,S,E,N); points must be clipped to Indonesia later.
BBOX = "94,-11.5,141.5,6.5"

def map_key():
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*FIRMS_MAP_KEY\s*=\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip('"').strip("'")
    raise SystemExit("FIRMS_MAP_KEY not found in .env")

def redact(text, key):
    return text.replace(key, "<MAP_KEY>")
