from prometheus_client import start_http_server, Gauge
import random
import time
from cdn_requests import *

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    nodes = []
    jitter = 0

    while True:
       nodes = cdn_fetch()
       RTT(nodes)
       jitter = random.randint(60,120)
       time.sleep(jitter)
