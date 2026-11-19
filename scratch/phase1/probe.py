import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sys, requests
from firms_common import BASE, BBOX, map_key, redact
k = map_key()
src, days, date = sys.argv[1], sys.argv[2], sys.argv[3]
r = requests.get(f"{BASE}/api/area/csv/{k}/{src}/{BBOX}/{days}/{date}", timeout=120)
t = redact(r.text, k)
lines = t.splitlines()
print("HTTP", r.status_code, "rows", len(lines)-1, "bytes", len(r.content))
print("\n".join(lines[:4]))
s = requests.get(f"{BASE}/mapserver/mapkey_status/", params={"MAP_KEY": k}, timeout=60)
print(redact(s.text, k))
