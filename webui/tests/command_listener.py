import zmq
import datetime

ctx = zmq.Context()
socket = ctx.socket(zmq.PAIR)
socket.connect('tcp://localhost:5508')

try:
    while True:
        msg = socket.recv_json()
        now = datetime.datetime.now().timestamp()
        print(now, msg)
finally:
    socket.close()
