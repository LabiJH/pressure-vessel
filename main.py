from prometheus_client import start_http_server, Gauge
import random
import time
from cdn_requests import *

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)

    while True:
       cdn_fetch()
       time.sleep(30)
