from asyncio.tasks import sleep
import random
import time
from prometheus_client import start_http_server, Gauge
import requests

# Create a Prometheus gauge metric
cdn_load = Gauge('steam_cdn_weighted_load', 'Weighted load per Steam CDN server', ['host'])


def get_cdn_load():
    resp = requests.get('https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/')
    servers = resp.json()["response"]["servers"]
    for server in servers:
        host = server.get("host")
        load = server.get("weighted_load")
        if host is not None and load is not None:
            cdn_load.labels(host=host).set(load)
            print(cdn_load.labels)

if __name__ == '__main__':
    # Start the Prometheus HTTP server on port 8000
    start_http_server(8000)

    while True:
        # Generate a random number
        get_cdn_load()
        # Set the value of the Prometheus metric
        # random_number_metric.set()
        # Sleep for 30 sec
        time.sleep(30)
