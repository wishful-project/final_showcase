import zmq
import time
import datetime
import json
from random import random

ctx = zmq.Context()
socket = ctx.socket(zmq.PUB)
socket.connect('tcp://localhost:5506')


try:
    while True:
        ctrl = "WIFI_CNIT"
        now = datetime.datetime.now().timestamp()
        data = {
            "type": "monitorReport",
            "monitorType": "performance",
            "networkController": ctrl,
            "networkType": "80211",
            "monitorValue": {
                "timestamp": now,
                "PER": random(),
                "THR": random() * 1e6,
            },
        }
        socket.send_multipart([
            b'monitorReport',
            json.dumps(data).encode('utf-8'),
        ])
        print(now, ctrl)
        time.sleep(0.5)
finally:
    socket.close()
