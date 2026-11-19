"""Download BIG 'Area Batas Wilayah Administrasi Kabupaten/Kota' (edisi Juni 2026) as GeoJSON pages.
Server-side generalization via maxAllowableOffset (degrees). One-off Phase 1 script."""
import sys, json, time, hashlib, pathlib, requests
REPO = pathlib.Path(__file__).resolve().parents[2]
URL = "https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_KABKOTA_AR/MapServer/0/query"
offset = sys.argv[1] if len(sys.argv) > 1 else "0.001"
out = REPO / "data" / "boundaries" / f"big_kabkota_2026_06_off{offset}"; out.mkdir(parents=True, exist_ok=True)
ids = requests.get(URL, params={"where": "1=1", "returnIdsOnly": "true", "f": "json"}, timeout=120).json()["objectIds"]
ids.sort(); print("features", len(ids), flush=True)
fields = "OBJECTID,NAMOBJ,KDPPUM,WADMPR,KDPKAB,WADMKK,TIPADM,LUASWH,METADATA"
for i in range(0, len(ids), 25):
    chunk = ids[i:i+25]; f = out / f"part_{i:04d}.geojson"
    if f.exists(): continue
    for attempt in range(5):
        try:
            r = requests.post(URL, data={"objectIds": ",".join(map(str, chunk)), "outFields": fields, "returnGeometry": "true",
                              "maxAllowableOffset": offset, "geometryPrecision": "6", "outSR": "4326", "f": "geojson"}, timeout=300)
            d = r.json()
            if len(d.get("features", [])) == len(chunk): break
            print("short", i, len(d.get("features", [])), str(d)[:200], flush=True)
        except Exception as e:
            print("err", i, str(e)[:200], flush=True)
        time.sleep(10 * (attempt + 1))
    else:
        raise SystemExit(f"failed at {i}")
    f.write_bytes(r.content); print(i, len(r.content), flush=True)
print("DONE")
