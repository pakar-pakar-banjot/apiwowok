import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json, requests
from firms_common import BASE, map_key, redact
k = map_key()
r = requests.get(f"{BASE}/mapserver/mapkey_status/", params={"MAP_KEY": k}, timeout=60)
print(r.status_code, redact(r.text, k)[:500])
