import logging
import time
import zmq

from queue import Empty
from queue import Queue

action_queue = Queue()


def action_trigger(endpoint, q: Queue):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(endpoint)

    while True:
        try:
            task = q.get_nowait()
            logging.debug(task)
            socket.send_json(task)
        except Empty:
            time.sleep(1)
