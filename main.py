from prometheus_client import start_http_server, Gauge
import random
import time
from cdn_requests import *

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    nodes = []

    while True:
        try:
            nodes = cdn_fetch()
            RTT(nodes)
            time.sleep(random.randint(60,120))
        except Exception as e:
            print(e)
            time.sleep(30)
