import zmq
import time
import datetime
import json
import random

ctrls = (
    'WIFI_CNIT',
    'WIFI_IMEC',
    'WIFI_something',
    'ZigBee_net',
    'LTE_net',
)

ctx = zmq.Context()
socket = ctx.socket(zmq.PUB)
socket.connect('tcp://localhost:5506')


try:
    while True:
        now = datetime.datetime.now().timestamp()
        for ctrl in ctrls:
            data = {
                "type": "monitorReport",
                "monitorType": "performance",
                "networkController": ctrl,
                "networkType": "80211",
                "monitorValue": {
                    "timestamp": now,
                    "PER": random.random(),
                    "THR": random.random() * 1e6,
                },
            }
            socket.send_multipart([
                b'monitorReport',
                json.dumps(data).encode('utf-8'),
            ])
            print(now, ctrl)
        time.sleep(0.6)
finally:
    socket.close()
