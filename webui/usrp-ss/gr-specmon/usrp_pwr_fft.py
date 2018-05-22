#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: USRP Spectrum Monitor
# Author: Mikołaj Chwalisz
# Generated: Wed Apr 11 15:29:56 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from optparse import OptionParser
import time
import waterfall_zmq_sink


class usrp_pwr_fft(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "USRP Spectrum Monitor")

        ##################################################
        # Variables
        ##################################################
        self.usrp_addr = usrp_addr = "192.168.20.2"
        self.samp_rate = samp_rate = 22e6
        self.frame_rate = frame_rate = 0.001
        self.fft_size = fft_size = 128
        self.center_freq = center_freq = 2.462e9

        ##################################################
        # Blocks
        ##################################################
        self.waterfall_zmq_sink = waterfall_zmq_sink.blk(freq_Size=fft_size, num_Samples=1000, msg_interval=1000)
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
        	",".join(("type=b200", '')),
        	uhd.stream_args(
        		cpu_format="fc32",
        		otw_format='sc16',
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0_0.set_gain(30, 0)
        (self.uhd_usrp_source_0_0).set_min_output_buffer(2024)
        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
        	sample_rate=samp_rate,
        	fft_size=fft_size,
        	ref_scale=2,
        	frame_rate=1000,
        	avg_alpha=1.0,
        	average=False,
        )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, fft_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_float*1, fft_size)
        (self.blocks_stream_to_vector_0).set_min_output_buffer(2024)
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_float*1, (fft_size/2, fft_size/2))
        self.blocks_deinterleave_0 = blocks.deinterleave(gr.sizeof_float*1, fft_size/2)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_deinterleave_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.blocks_deinterleave_0, 1), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.waterfall_zmq_sink, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_deinterleave_0, 0))
        self.connect((self.logpwrfft_x_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.logpwrfft_x_0, 0))

    def get_usrp_addr(self):
        return self.usrp_addr

    def set_usrp_addr(self, usrp_addr):
        self.usrp_addr = usrp_addr

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)
        self.logpwrfft_x_0.set_sample_rate(self.samp_rate)

    def get_frame_rate(self):
        return self.frame_rate

    def set_frame_rate(self, frame_rate):
        self.frame_rate = frame_rate

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_source_0_0.set_center_freq(self.center_freq, 0)


def main(top_block_cls=usrp_pwr_fft, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
