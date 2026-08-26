import random
import time
import re
from ssl import SSLError

import requests
from prometheus_client import Gauge, Histogram


DISCOVERY_INTERVAL = 600  # re-run full discovery every 10 minutes
HEADERS = {
    'User-Agent': 'pressurevessel/0.1 (+https://github.com/LabiJH/pressurevessel; monitoring probe, low-frequency)',
}
API_URL = "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/"
REGION_RE = re.compile(r'cache\d+-([a-z0-9-]+)\.steamcontent\.com')
POP_COORDS = {
    "fra1": (50.11, 8.68),
    "fra2": (50.11, 8.68),
    "lhr1": (51.51, -0.13),
    "par1": (48.85, 2.35),
    "ams1": (52.37, 4.90),
    "vie1": (48.21, 16.37),
    "sto1": (59.33, 18.06),
    "sto2": (59.33, 18.06),
    "waw1": (52.23, 21.01),
    "iev-giga": (50.45, 30.52),
    "jnb1": (-26.20, 28.05),
    "tyo3": (35.68, 139.69),
    "hkg1": (22.32, 114.17),
    "sgp1": (1.35, 103.82),
    "syd1": (-33.87, 151.21),
    "iad1": (39.04, -77.49),
    "ord1": (41.88, -87.63),
    "atl3": (33.75, -84.39),
    "dfw2": (32.78, -96.80),
    "sea1": (47.61, -122.33),
    "lax1": (34.05, -118.24),
    "lax2": (34.05, -118.24),
    "gru1": (-23.55, -46.63),
}

steam_cdn_pop_info = Gauge('steam_cdn_pop_info', 'POP coordinates', ['region', 'lat', 'lon'])
host_last_seen = Gauge('steam_cdn_host_last_seen_timestamp', 'Unix timestamp this host last appeared in a scrape', ['host'])
http_response_time = Gauge('steam_cdn_http_response_time', 'HTTP Response time per Node', ['host', 'region'])
http_response_time_hist = Histogram(
    'steam_cdn_http_response_time_seconds',
    'HTTP response time per Steam CDN region',
    ['region'],
    buckets=[0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 2.0, 5.0],
)
_cached_hosts = []
_last_discovery = 0

def region_from_host(host: str) -> str:
    m = REGION_RE.match(host)
    return m.group(1) if m else 'other'

def cdn_fetch(force_refresh: bool = False) -> list:
    global _cached_hosts, _last_discovery
    now = time.time()
    if not force_refresh and _cached_hosts and (now - _last_discovery) < DISCOVERY_INTERVAL:
        return _cached_hosts  # skip the 100 API calls entirely

    hostnames = []

    # Cell_IDs are UNDOCUMENTED, up to 100 is an educated guess from what is known currently.
    for i in range(0, 100):
        try:
            response = requests.get(API_URL, {"cell_id": i}, timeout=10.0, headers=HEADERS)
            data = response.json()
            # 'server' == dictionary in the servers list
            for server in data["response"]["servers"]:
                if server["type"] != "CDN":
                    host_last_seen.labels(server["host"]).set(now)
                if server["host"] not in hostnames:
                    hostnames.append(server["host"])

        except Exception as e:
            print(f"[skip] cell {i} failed: {e.__class__.__name__}: {e}")
            continue

        time.sleep(random.uniform(0.2, 0.4))

    for region, (lat,lon) in POP_COORDS.items():
       steam_cdn_pop_info.labels(region=region, lat=str(lat), lon=str(lon)).set(1)

    _cached_hosts = hostnames
    _last_discovery = now
    return hostnames


# Calculate RTT for each CDN POP
def RTT(url_list: list):
    print("[RTT] Checking HTTP RTT...")

    for hosts in url_list:
        jitter = random.uniform(0.2, 0.4)
        time.sleep(jitter)
        try:
            region = region_from_host(hosts)
            t1 = time.time()
            requests.get(f'https://{hosts}', timeout=10.0, headers=HEADERS)
            t2 = time.time()
            ttt = (t2 - t1) * 1000
            http_response_time.labels(hosts, region).set(ttt)
            http_response_time_hist.labels(region).observe(ttt / 1000)
            print(f"HTTPS response time for {hosts} : {ttt:.2f}ms")

        except requests.exceptions.SSLError:
            try:
                t1 = time.time()
                r = requests.get(f'http://{hosts}', timeout=10.0, headers=HEADERS)
                t2 = time.time()
                ttt = (t2 - t1) * 1000
                http_response_time.labels(hosts, region).set(ttt)
                http_response_time_hist.labels(region).observe(ttt / 1000)
                print(f"HTTP response time for {hosts} : {ttt:.2f}ms")
            except Exception as e:
                print(e)

        except requests.exceptions.RequestException as e:
            print(f"[skip] {hosts} failed: {e.__class__.__name__}: {e}")
            continue

    print("[RTT] Success!")
