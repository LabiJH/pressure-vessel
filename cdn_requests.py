import random
import time
import re
from ssl import SSLError

import requests
from prometheus_client import Gauge, Histogram

API_URL = "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/"
REGION_RE = re.compile(r'cache\d+-([a-z0-9-]+)\.steamcontent\.com')

host_last_seen = Gauge('steam_cdn_host_last_seen_timestamp', 'Unix timestamp this host last appeared in a scrape', ['host'])
http_response_time = Gauge('steam_cdn_http_response_time', 'HTTP Response time per Node', ['host'])
http_response_time_hist = Histogram(
    'steam_cdn_http_response_time_seconds',
    'HTTP response time per Steam CDN region',
    ['region'],
    buckets=[0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 2.0, 5.0],
)

def region_from_host(host: str) -> str:
    m = REGION_RE.match(host)
    return m.group(1) if m else 'other'

def cdn_fetch() -> list:
    now = time.time()
    hostnames = []

    for i in range(0, 100):
        response = requests.get(API_URL, {"cell_id": i})
        data = response.json()

        # 'server' == dictionary in the servers list
        for server in data["response"]["servers"]:
            if server["type"] != "CDN":
                host_last_seen.labels(server["host"]).set(now)
            if server["host"] not in hostnames:
                hostnames.append(server["host"])

        time.sleep(random.uniform(0.2, 0.4))

    return hostnames


# Calculate RTT for each CDN POP
def RTT(url_list: list):

    for hosts in url_list:
        jitter = random.uniform(0.2, 0.4)
        time.sleep(jitter)
        try:
            region = region_from_host(hosts)
            jitter = random.randint(1, 4)
            t1 = time.time()
            r = requests.get(f'https://{hosts}', timeout=10.0)
            t2 = time.time()
            ttt = (t2 - t1) * 1000
            http_response_time.labels(hosts).set(ttt)
            http_response_time_hist.labels(region).observe(ttt / 1000)
            print(f"HTTPS response time for {hosts} : {ttt:.2f}ms")

        except requests.exceptions.SSLError:
            t1 = time.time()
            r = requests.get(f'http://{hosts}', timeout=10.0)
            t2 = time.time()
            ttt = (t2 - t1) * 1000
            http_response_time.labels(hosts).set(ttt)
            http_response_time_hist.labels(region).observe(ttt / 1000)
            print(f"HTTP response time for {hosts} : {ttt:.2f}ms")

        except requests.exceptions.RequestException as e:
            print(f"[skip] {hosts} failed: {e.__class__.__name__}: {e}")
            continue
