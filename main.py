<<<<<<< HEAD
from asyncio.tasks import sleep
import random
import time
from prometheus_client import start_http_server, Gauge
import requests


CELL_IDS = {
    1: "ord", 4: "lhr", 5: "fra", 14: "par", 15: "ams",
    25: "gru", 31: "sea", 32: "tyo", 33: "hkg", 35: "sgp",
    38: "waw", 40: "mad", 50: "atl", 52: "syd", 63: "iad",
    64: "lax", 65: "dfw", 66: "sto", 92: "vie",
}

# Create a Prometheus gauge metric
scrape_success = 0
server_count = 0

# Prometheus Metrics
cdn_load = Gauge('steam_cdn_weighted_load', 'Weighted load per Steam CDN server', ['host', 'region'])
scrape_success = Gauge("steam_cdn_scrape_success", "Was the cell sucessfully scraped in the last cycle", ['cell_id', 'region'])
returned_servers = Gauge("steam_cdn_servers_returned", "Count of returned servers per cell", ['cell_id', 'region'])

known_servers = {}

def fetch_cell(cell_id):
    resp = requests.get(
        "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/",
        params={"cell_id": cell_id, "max_servers": 100},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["response"]["servers"]

def scrape_cycle():
    for cell_id, region in CELL_IDS.items():
        try:
            servers = fetch_cell(cell_id)
        except requests.RequestException:
            scrape_success.labels(cell_id=cell_id, region=region).set(0)
            continue  # keep whatever we already had for this region

        scrape_success.labels(cell_id=cell_id, region=region).set(1)

        now = time.time()
        for s in servers:
            host = s.get("host")
            load = s.get("weighted_load")
            if host is None:
                continue
            known_servers[host] = {"region": region, "weighted_load": load, "last_seen": now}
            if load is not None:
                cdn_load.labels(host=host, region=region).set(load)

        time.sleep(0.5)  # space out the 19 calls a bit — cheap insurance against self-inflicted throttling

if __name__ == '__main__':
    # Start the Prometheus HTTP server on port 8000
    start_http_server(8000)

    while True:
        scrape_cycle()
        time.sleep(30)
=======
from prometheus_client import start_http_server, Gauge
import random
import time
from cdn_requests import *

# Create a metric to track time spent and requests made.

test_value = Gauge('steam_cdn_load', 'CDN Hostname + Load', ['hostname', 'load'])

# Decorate function with metric.

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
       cdn_fetch(test_value)
       time.sleep(10)
>>>>>>> 31f1b27 (Added logic for getting CDN Response and creating gauge)
