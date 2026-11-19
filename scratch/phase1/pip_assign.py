"""Assign unique FIRMS coordinates to BIG kab/kota polygons (edisi Juni 2026, generalized 0.001 deg).
Pure numpy even-odd ray casting. Writes data/firms/profile/coord_assign.csv.
For unassigned points, computes distance (km, equirectangular approx) to nearest polygon edge within 0.1 deg."""
import sys, pathlib, csv, glob, json, time
import numpy as np
REPO = pathlib.Path(__file__).resolve().parents[2]
BDIR = REPO / "data" / "boundaries" / "big_kabkota_2026_06_off0.001"
RAW = REPO / "data" / "firms" / "raw"
OUT = REPO / "data" / "firms" / "profile"; OUT.mkdir(parents=True, exist_ok=True)

feats = []
for p in sorted(BDIR.glob("*.geojson")):
    feats += json.loads(p.read_text(encoding="utf-8"))["features"]
parts = []  # (feat_idx, edges array (m,4), bbox)
for i, f in enumerate(feats):
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        segs = []
        for ring in poly:
            r = np.asarray(ring, dtype=np.float64)[:, :2]
            segs.append(np.hstack([r[:-1], r[1:]]))
        e = np.vstack(segs)
        bb = (e[:, [0, 2]].min(), e[:, [1, 3]].min(), e[:, [0, 2]].max(), e[:, [1, 3]].max())
        parts.append((i, e, bb))
print("features", len(feats), "parts", len(parts), flush=True)

coords = set()
for f in RAW.glob("*/*.csv"):
    with open(f, encoding="utf-8") as fh:
        rd = csv.reader(fh); h = next(rd); ia, io_ = h.index("latitude"), h.index("longitude")
        for row in rd:
            if row: coords.add((row[ia], row[io_]))
coords = sorted(coords)
lat = np.array([float(a) for a, _ in coords]); lon = np.array([float(b) for _, b in coords])
print("unique coords", len(coords), flush=True)
order = np.argsort(lon); slon = lon[order]
assign = np.full(len(coords), -1, dtype=np.int64); nhit = np.zeros(len(coords), dtype=np.int32)
t0 = time.time()
def inside(px, py, e):
    res = np.zeros(len(px), dtype=bool)
    x1, y1, x2, y2 = e[:, 0], e[:, 1], e[:, 2], e[:, 3]
    step = max(1, int(2e7 // max(len(e), 1)))
    for s in range(0, len(px), step):
        X = px[s:s+step, None]; Y = py[s:s+step, None]
        c = ((y1 > Y) != (y2 > Y))
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (x2 - x1) * (Y - y1) / (y2 - y1) + x1
        res[s:s+step] = (np.count_nonzero(c & (X < xint), axis=1) % 2) == 1
    return res
for fi, e, (x0, y0, x1_, y1_) in parts:
    a, b = np.searchsorted(slon, [x0, x1_], side="left")[0], np.searchsorted(slon, x1_, side="right")
    if b <= a: continue
    idx = order[a:b]; idx = idx[(lat[idx] >= y0) & (lat[idx] <= y1_)]
    if len(idx) == 0: continue
    ins = inside(lon[idx], lat[idx], e); hit = idx[ins]
    nhit[hit] += 1; assign[hit] = np.where(assign[hit] < 0, fi, assign[hit])
print("pip done %.1fs, assigned %d, multi %d" % (time.time() - t0, (assign >= 0).sum(), (nhit > 1).sum()), flush=True)

# distance for unassigned points to nearest edge within 0.1 deg
un = np.where(assign < 0)[0]; dist = np.full(len(coords), np.nan); near = np.full(len(coords), -1, dtype=np.int64)
R = 0.1
for fi, e, (x0, y0, x1_, y1_) in parts:
    a, b = np.searchsorted(slon, x0 - R, side="left"), np.searchsorted(slon, x1_ + R, side="right")
    if b <= a: continue
    idx = order[a:b]; idx = idx[(assign[idx] < 0) & (lat[idx] >= y0 - R) & (lat[idx] <= y1_ + R)]
    if len(idx) == 0: continue
    step = max(1, int(1e7 // len(e)))
    for s in range(0, len(idx), step):
        ii = idx[s:s+step]; px = lon[ii, None]; py = lat[ii, None]
        kx = np.cos(np.radians(py)) * 111.32; ky = 110.57
        ax, ay = e[:, 0] * 1, e[:, 1]; bx, by = e[:, 2], e[:, 3]
        dx, dy = (bx - ax) * kx, (by - ay) * ky; qx, qy = (px - ax) * kx, (py - ay) * ky
        L = dx * dx + dy * dy
        t = np.clip(np.where(L > 0, (qx * dx + qy * dy) / np.where(L > 0, L, 1), 0), 0, 1)
        d = np.sqrt((qx - t * dx) ** 2 + (qy - t * dy) ** 2).min(axis=1)
        better = np.isnan(dist[ii]) | (d < dist[ii])
        dist[ii[better]] = d[better]; near[ii[better]] = fi
print("distance done %.1fs" % (time.time() - t0), flush=True)
with open(OUT / "coord_assign.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["latitude", "longitude", "kdppum", "wadmpr", "kdpkab", "wadmkk", "n_hits", "nearest_kdppum", "nearest_km"])
    for j, (a, b) in enumerate(coords):
        p = feats[assign[j]]["properties"] if assign[j] >= 0 else None
        q = feats[near[j]]["properties"] if near[j] >= 0 else None
        w.writerow([a, b, p["KDPPUM"] if p else "", p["WADMPR"] if p else "", (p["KDPKAB"] or "").strip() if p else "",
                    p["WADMKK"] if p else "", nhit[j], q["KDPPUM"] if q else "", "" if np.isnan(dist[j]) else round(float(dist[j]), 3)])
print("DONE")
