import requests
from prometheus_client import Gauge

API_URL = "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/"
PARAMS = {"cell_id": 5}

def cdn_fetch(gauge: Gauge):
    response = requests.get(API_URL,params=PARAMS)
    json = response.json()
    # 'key' == dictionary in the servers list
    for key in json["response"]["servers"]:
        print(key["host"])
        gauge.labels(key["host"], key["weighted_load"]).inc()
