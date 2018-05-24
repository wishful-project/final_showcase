import json
import logging
import zmq
import numpy as np
import conf

from datetime import datetime
from functools import partial
from tornado import gen


@gen.coroutine
def plt_update(source, timestamp, THR, PER):
    source.stream(dict(
        timestamp=[datetime.fromtimestamp(timestamp)],
        THR=[THR],
        PER=[PER],
    ), 120)


@gen.coroutine
def tab_update(source, data):
    source.data = data


def stats_listener(endpoint, server_context):
    logging.info('Starting statistics listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'monitorReport')
    socket.setsockopt(zmq.SUBSCRIBE, b'networkStatusUpdate')
    socket.bind(endpoint)

    while True:
        full_msg = socket.recv_multipart()

        msg = json.loads(full_msg[1].decode('utf-8'), encoding='utf-8')

        print(msg)

        if full_msg[0] == b'monitorReport':
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    plt_update,
                    source=ses._document.select_one(
                        {'name': msg['networkController']}),
                    timestamp=msg['monitorValue']['timestamp'],
                    THR=msg['monitorValue']['THR'],
                    PER=msg['monitorValue']['PER'],
                ))
        if full_msg[0] == b'networkStatusUpdate':
            for ses in server_context.application_context.sessions:
                ses._document.add_next_tick_callback(partial(
                    tab_update,
                    source=ses._document.select_one(
                        {'name': 'networkStatusUpdate'}),
                    data=dict(
                        name=[x['name'] for x in msg if x['active'] is True],
                        type=[x['type'] for x in msg if x['active'] is True],
                        channel=[x['channel'] for x in msg
                            if x['active'] is True],
                        load=[x['load'] for x in msg if x['active'] is True],
                    ),
                ))


@gen.coroutine
def usrp_plot_update(source, spectrogram):
    source.update(data=dict(spectrogram=[spectrogram]))


@gen.coroutine
def usrp_fig_update(source, fc, bw, size):
    source.update(data=dict(fc=[fc], bw=[bw], size=[size]))


def usrp_listener(endpoint, server_context):
    logging.info('Starting USRP listener on %s', endpoint)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'gnuradio.spectrogram')
    socket.bind(endpoint)

    while True:
        full_msg = socket.recv_multipart()

        info = json.loads(full_msg[1])
        spectrogram = np.frombuffer(full_msg[2], dtype=np.float32).reshape(
            int(info['l']), int(info['w']))

        for ses in server_context.application_context.sessions:
            ses._document.add_next_tick_callback(partial(
                usrp_plot_update,
                source=ses._document.select_one({'name': 'spectrogram'}),
                spectrogram=spectrogram,
            ))

            fc = int(info['fc'])
            bw = int(info['bw'])
            size = int(info['l'])
            ses._document.add_next_tick_callback(partial(
                usrp_fig_update,
                source=ses._document.select_one(
                    {'name': 'spectrogram_vars'}),
                fc=fc,
                bw=bw,
                size=size,
            ))
