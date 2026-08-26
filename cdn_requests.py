from ssl import SSLError

import requests, time
from prometheus_client import Gauge

API_URL = "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/"

test_value = Gauge('steam_cdn_load', 'CDN Hostname + Load', ['hostname', 'load'])
host_last_seen = Gauge('steam_cdn_host_last_seen_timestamp', 'Unix timestamp this host last appeared in a scrape', ['host'])
http_response_time = Gauge('steam_cdn_http_response_time', 'HTTP Response time per Node', ['host'])

def cdn_fetch():
    now = time.time()
    hostnames = []
    for i in range(0,100):
        response = requests.get(API_URL,{"cell_id":i})
        json = response.json()
        # 'key' == dictionary in the servers list
        for key in json["response"]["servers"]:
            if key["type"] != "CDN":
            #    print(key["host"])
                test_value.labels(key["host"], key["weighted_load"]).set(key["weighted_load"])
                host_last_seen.labels(key["host"]).set(now)
            if key["host"] not in hostnames:
                hostnames.append(key["host"])
        time.sleep(0.5)
    print(len(hostnames))
    RTT(hostnames)

# Calculate RTT for each CDN POP
def RTT(url_list):

    for hosts in url_list:
        try:
                t1 = time.time()
                r = requests.get(f'https://{hosts}')
                t2 = time.time()
                ttt = (t2-t1) * 1000
                http_response_time.labels(hosts).set(ttt)
                print(f"HTTPS response time for {hosts} : {ttt:.2f}ms")
        except requests.exceptions.SSLError:
                t1 = time.time()
                r = requests.get(f'http://{hosts}')
                t2 = time.time()
                ttt = (t2-t1) * 1000
                http_response_time.labels(hosts).set(ttt)
                print(f"HTTP response time for {hosts} : {ttt:.2f}ms")
