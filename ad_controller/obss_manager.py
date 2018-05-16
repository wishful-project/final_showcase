
import logging

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class ObssManager(object):
    """ObssManager"""
    def __init__(self):
        super(ObssManager, self).__init__()
        self.networks = []
        self.pubSocket = None

    def set_pub_socket(self, pubSocket):
        self.pubSocket = pubSocket

    def add_network(self, network):
        self.networks.append(network)

        print("Managed WiFi networks")
        for n in self.networks:
            print(n.name, n.networkType)

    def notify_command_msg(self, cmdMsg):
        print("ObssManager: Received Command Message")
        print(cmdMsg)

    def notify_channel_usage(self, channelUsage):
        print("ObssManager: Received Channel Usage Report")
        print(channelUsage)

    def notify_interference_report(self, interferenceReport):
        print("ObssManager: Received Interference Report")
        print(interferenceReport)

    def notify_performance_report(self, perfomanceReport):
        print("ObssManager: Received Performance Report")
        print(perfomanceReport)
