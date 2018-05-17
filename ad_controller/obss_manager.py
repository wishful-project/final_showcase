import time
import json
import struct

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class WiFiNetwork(object):
    """docstring for WiFiNetwork"""
    def __init__(self, netId, ctrName, netType, solutionList,
                 cmdList, monList):
        super(WiFiNetwork, self).__init__()
        self.netId = netId
        self.ctrName = ctrName
        self.netType = netType
        self.solutionList = solutionList
        self.cmdList = cmdList
        self.monList = monList

        self.activated = False

        self.channel = None
        self.frequency = None
        self.bandwidth = None
        self.lastChanSwitchTime = time.time()

        self.requestedTraffic = 0.0
        self.currentTraffic = 0.0
        self.performance = 0
        self.satisfied = True
        # throughput on each channel
        self.throughputCache = {}

    def send_switch_channel_cmd(self, socket, newChannel):
        msg = {'type': 'publisherUpdate',
               'involvedController': [self.ctrName],
               'commandList': {'WiFi_Channel_Switching': {'SWITCH_CHANNEL': {"channel": newChannel}}
                               }
               }

        print("SENT Switch command: ", msg)
        key = b"generic"
        seq_s = struct.pack('!l', 0)
        body = json.dumps(msg).encode('utf-8')
        socket.send_multipart([key, seq_s, body])


class ObssManager(object):
    """ObssManager"""
    def __init__(self):
        super(ObssManager, self).__init__()
        self.networks = []
        self.wifiNetworks = {}
        self.pubSocket = None
        self.minChanSwitchInterval = 10
        self.avaiableChannels = [1, 6, 11]

    def set_pub_socket(self, pubSocket):
        self.pubSocket = pubSocket

    def get_active_networks(self,):
        activeNets = []
        for name, net in self.wifiNetworks.items():
            if net.activated:
                activeNets.append(net)

        return activeNets

    def _perform_optimization(self):
        activeNets = self.get_active_networks()
        activeNetNumber = len(activeNets)
        print("Number of active networks: ", activeNetNumber)
        for n in activeNets:
            print("---Net: ", n.ctrName,
                  " Channel: ", n.channel,
                  " Traffic: ",
                  " Requested: ", n.requestedTraffic,
                  " Current: ", n.currentTraffic)

        if activeNetNumber == 0:
            # do nothing
            return

        # check if active networks are satisfied with current traffic
        for n in activeNets:
            # if no traffic do nothing
            if n.requestedTraffic == 0:
                return

            if n.currentTraffic > 0.7 * n.requestedTraffic:
                n.satisfied = True
            else:
                n.satisfied = False

        if activeNetNumber == 1:
            net0 = activeNets[0]
            if net0.satisfied:
                # do nothing
                return
            else:
                # find channel with the best performance
                newChannelIdx = self.avaiableChannels.index(net0.channel) + 1
                if newChannelIdx >= len(self.avaiableChannels):
                    newChannelIdx = 0

                newChannel = self.avaiableChannels[newChannelIdx]
                now = time.time()
                if now - net0.lastChanSwitchTime > self.minChanSwitchInterval:
                    net0.send_switch_channel_cmd(self.pubSocket, newChannel)
                    net0.channel = newChannel
                    net0.lastChanSwitchTime = now

        elif activeNetNumber == 2:
            # manage networks
            net0 = activeNets[0]
            net1 = activeNets[1]

            if net0.satisfied and net1.satisfied:
                # do nothing
                return

    def add_network(self, network):
        self.networks.append(network)
        wifiNetwork = WiFiNetwork(network.id, network.name,
                                  network.networkType,
                                  network.solution,
                                  network.commandList,
                                  network.monitorList)

        self.wifiNetworks[network.name] = wifiNetwork

        print("ObssManager: Managed WiFi networks")
        for name, net in self.wifiNetworks.items():
            print(net.netId, net.ctrName)

    def notify_command_msg(self, cmdMsg):
        print("ObssManager: Received Command Message")
        print(cmdMsg)

        ctrName = cmdMsg["involvedController"][0]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        cmdList = cmdMsg["commandList"]
        cmds = cmdList["WiFi_Channel_Switching"]

        for commandName, commandParameters in cmds.items():
            print("ObssManager: Received Command Message: ", commandName)

            trafficSize = None

            if commandName == "ACTIVATE":
                network.activated = True
            elif commandName == "DEACTIVATE":
                network.activated = False
            elif commandName == "SWITCH_CHANNEL":
                pass

            # traffic commands
            elif commandName == "TRAFFIC":
                trafficSize = commandParameters["TYPE"]
            elif commandName == "TRAFFIC_SET_OFF":
                trafficSize = "OFF"
            elif commandName == "TRAFFIC_SET_LOW":
                trafficSize = "LOW"
            elif commandName == "TRAFFIC_SET_MEDIUM":
                trafficSize = "MEDIUM"
            elif commandName == "TRAFFIC_SET_HIGH":
                trafficSize = "HIGH"

            if trafficSize:
                requestedTraffic = 0
                if trafficSize == "OFF":
                    requestedTraffic = 0
                elif trafficSize == "LOW":
                    requestedTraffic = 1
                elif trafficSize == "MEDIUM":
                    requestedTraffic = 20
                elif trafficSize == "HIGH":
                    requestedTraffic = 100

                network.requestedTraffic = requestedTraffic
                # stay on the channel for a while
                # to measure the performance
                network.lastChanSwitchTime = time.time()

    def notify_channel_usage(self, channelUsageMsg):
        print("ObssManager: Received Channel Usage Report")
        print(channelUsageMsg)

        ctrName = channelUsageMsg["networkController"]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        values = channelUsageMsg["monitorValue"]
        freqUsage = values["frequencies"]
        channelUsage = values["channels"]

        oldChannel = network.channel
        try:
            network.channel = channelUsage[0]
            network.frequency = list(freqUsage.keys())[0]
            network.bandwidth = list(freqUsage.values())[0]
        except Exception:
            network.channel = None
            network.frequency = None
            network.bandwidth = None

        if oldChannel is None and network.channel is not None:
            # stay on the channel for a while
            network.lastChanSwitchTime = time.time()

    def notify_interference_report(self, interferenceReport):
        print("ObssManager: Received Interference Report")
        print(interferenceReport)

        # TODO: check if interferences overlap with used channels

    def notify_performance_report(self, perfomanceReport):
        print("ObssManager: Received Performance Report")
        print(perfomanceReport)

        ctrName = perfomanceReport["networkController"]
        network = self.wifiNetworks.get(ctrName, None)
        if network is None:
            return

        values = perfomanceReport["monitorValue"]
        performance = values["PER"]
        throughput = values["THR"]

        network.performance = performance
        network.currentTraffic = throughput

        # cache performance
        network.throughputCache[network.channel] = {"timestamp": time.time(),
                                                    "throughput": throughput}

        if network.channel is None:
            # wait for first channel usage report
            return

        self._perform_optimization()
