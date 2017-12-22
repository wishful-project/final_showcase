#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage:
   controller [options] [-q | -v]

Options:
   --logfile name	   Name of the logfile
   --config configFile Config file path
   --nodes name for nodes setup
   --experiment_info name experiment setup

Example:
   ./

Other options:
   -h, --help		   show this help message and exit
   -q, --quiet		   print less text
   -v, --verbose	   print more text
   --version		   show version and exit
"""

import datetime
import logging
import gevent
import os
import sys
import time
from itertools import cycle
import math
import json
import zmq
import yaml
import threading

sys.path.append('../')
sys.path.append('../../')
sys.path.append("../../agent_modules/iperf/")
sys.path.append("../../agent_modules/module_srslte/")
sys.path.append('../../upis')
sys.path.append('../../framework')
sys.path.append('../../agent')
sys.path.append('../../controller')
sys.path.append('../../controller_modules')

import wishful_controller
import wishful_upis as upis
from helper.MeasurementManager import MeasurementCollector
from lib.kvsimple import KVMsg
from local_control_program import remote_control_program
import wishful_module_srslte

__author__ = "Domenico Garlisi, ...."
__copyright__ = "Copyright (c) ..., "
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it; ..."


# """
# Setting of controller node
# """
# controller_PC_IP_address = "192.168.5.64"
# controller_PC_interface = "ens3"
# """
# END setting of controller nodes
# """
#
# DL_address = "tcp://" + controller_PC_IP_address + ":8990"
# UL_address = "tcp://" + controller_PC_IP_address + ":8989"
#
#
# """ START Define logging controller """
# """ we use the python logging system module (https://docs.python.org/2/library/logging.html) """
# log = logging.getLogger('wishful_controller')
#
# #Create controller, we specify in the parameters the ip addresses and the ports used for downlink and uplink connection
# #with the nodes tesbed, in this case we spcify the interface loopback and the port 8990 for the downlink and the
# # interface loopback and the port 8989 for the uplink.
# controller = wishful_controller.Controller(dl=DL_address, ul=UL_address)
#
# #Configure controller, we specify in the parameters the controller name and a string information related to the
# #controller
# controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")
#
# #add the discovery module, responsable for the nodes discovery procedure and nodes adding to the controllers
# #we specify interface, the name of the nodes group, and the ip address and port for the downlink and uplink connection
# controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
#                       className="PyreDiscoveryControllerModule",
#                       kwargs={"iface":controller_PC_interface, "groupName":"wishful_4321", "downlink":DL_address, "uplink":UL_address})
# """ END the WiSHFUL controller setting """

class WiFiNode():
    """
    This class defines an WiFi node in order to :
        Set wireless lan interface ip address and network role (Station/AccessPoint)
        Stores/Removes low level measurements
        Store the low level measurements type
    """
    def __init__(self, node, mac_address):
        """ Creates a new WiFiNode object
        """
        self.node = node
        self.wlan_ipAddress = '192.168.0.' + node.ip.split('.')[3]
        self.mac_address = mac_address
        self.measurements = []
        self.measurements_types = []
        self.role = None
        self.platform = None
        self.interface = None
        self.interference_class = []

    def add_measure(self, measure):
        """ Adds a measure or a list of measurable in the list of node measurement
        :param measure: list of measure to add at measurements object attribute
        """
        self.measurements.append(measure)

    def add_inferference_class(self, interf_class):
        """ Adds the predicted interference class
        :param class: the predicted interference class according to the classifier
        """
        self.interference_class.append(interf_class)

    def get_available_measures(self):
        """ Gets the available measure of the node
        :return measure_list: the list of measure stored until now
        """
        return self.measurements


log = logging.getLogger('wishful_agent.main')
controller = wishful_controller.Controller()

"""
Create MeasurementCollector object, to keep information about WiFiNode measurements and perform plotting result
"""
meas_collector = MeasurementCollector(log)

# Global list with all nodes (agents) connected to this controller. We start empty and append nodes when they start.
# See new_node function below
nodes = []
TOTAL_NODES = 1 # We expect 2 nodes to connect: 'tx', and 'rx'.

wifinodes = [] # list of WiSHFUL WiFI nodes
do_run = None # used to keep alive all the controller threads

@controller.new_node_callback()
def new_node(node):
    """ This function is performed when a new node has been found in the network

    :param node: finded node
    """
    nodes.append(node)
    print("New node appeared:")
    print(node)

@controller.node_exit_callback()
def node_exit(node, reason):
    """ This function is performed when a node, present in the controller node list, leave the experiment. During the
    experiment, the nodes send "hello packet" to the controller. If the controller do not receives hello packet from a node
    present in the node list, perform this function and the node is been removed

    :param node: node that leave the experiment
    :param reason : exit reason
    """
    # Safety check
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@controller.add_callback(upis.radio.get_parameters)
def get_vars_response(group, node, data):
    """ This function implements a callback called when ANY get_* function is called in ANY of the nodes

    :param group: Experiment group name
    :param node: Node used to execute the UPI
    :param data: ::TODO::
    """
    print("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

def print_response(group, node, data):
    """ This function implements a callback to print generic UPI function calling result

    :param group: Experiment group name
    :param node: Node used to execute the UPI
    :param data: Execution time
    """
    print("\n{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))


def register_solution_to_solution_global_controller(request):
    """
    ****	SETUP SOLUTION GLOBAL CONTROLLER CONNECTION	****
    This function is used to setup the connection with the experiment GUI,
    a ZMQ socket server is created on port 8500, able to receive command from GUI
    """
    #Register solution to solution global controller
    # Activation 	Event
    # De - activation
    # Event 	List 	of 	monitoring 	parameters
    # List 	of 	control knobs / parameters

    #create the json format message
    solutionName = 'lte_ct'
    commandList = ["ON", "OFF"]
    eventList = [""]
    msg = {"type": "registerRequest", "solution": solutionName, "commandList": commandList, "eventList": eventList}
    print('msg --> %s' % str(msg))

    #prepare the message
    sequence = 1
    kvmsg = KVMsg(sequence)
    kvmsg.key = b"generic"
    kvmsg.body = json.dumps(msg).encode('utf-8')
    #send the message
    kvmsg.send(request)

    #process the registerRespons
    #TOBE
    try:
        kvmsg_reply = KVMsg.recv(request)
    except:
        return False

    seq = kvmsg_reply.sequence
    key = kvmsg_reply.key
    body = kvmsg_reply.body
    print(body)
    parsed_json = json.loads(body.decode("utf-8"))
    if "type" in parsed_json:
        type = parsed_json["type"]
        if type == "registerResponse":
            print("Received registration respons")
            return True
    return False


def listener_subscriber(arg,subscriber):
    sequence = 0
    kvmap = {}
    while True:
        try:
            kvmsg = KVMsg.recv(subscriber)
        except KeyboardInterrupt:
            return
        except:
            break  # Interrupted
        if kvmsg.sequence > sequence:
            sequence = kvmsg.sequence
            print("*********")
            print("received update information with sequence %d" % sequence)
            print(kvmsg.body)
            print("*********")
            kvmsg.store(kvmap)

def start_command_connection():
    """
                    ****	SETUP COMMAND RECEIVER	****
    This function is used to setup the connection with the experiment GUI,
    a ZMQ socket server is created on port 8500, able to receive command from GUI
    """
    print(controller.name)
    socket_command_port = "8500"
    context = zmq.Context()
    socket_command = context.socket(zmq.PAIR)
    socket_command.bind("tcp://*:%s" % socket_command_port)
    print("Create server on port %s ... ready to receive command from experiment GUI" % socket_command_port)
    return socket_command

def start_visualizer_connection():
    """
                    ****	SETUP STATISTICS VISUALIZER	****
    This function is used to setup the connection with the experiment GUI,
    a ZMQ socket client is created on port 8501, able to send statistical information to GUI
    """
    print(controller.name)
    socket_visualizer_port = "8501"
    context = zmq.Context()
    socket_visualizer = context.socket(zmq.PUSH)
    socket_visualizer.connect("tcp://10.8.8.21:%s" % socket_visualizer_port)
    print("Connecting to server on port %s ... ready to send information to experiment GUI" % socket_visualizer_port)

    ''' 
    implement OML database setup for realtime visualizer 
    in a different case, we can send the statistica information to the OMLBase
    '''
    # global omlInst
    # omlInst = oml4py.OMLBase("LocalControlProgram", "WiSHFUL", socket.gethostname(),"tcp:am.wilab2.ilabt.iminds.be:3004")
    # omlInst.addmp("IEEE802154_MACSTATS", "timestamp:int32 nodeID:int32 packetSize:int32 activeRadioprogram:string timeDiff:int32 numTxRequest:int32 numTxRequestFail:int32 numTxAttempt:int32 numTxSuccess:int32 numTxFail:int32 numTxBusy:int32 numTxNoAck:int32 numTxCollision:int32 numRx:int32 avgBackoffExponent:int32")
    # omlInst.start()

    return socket_visualizer

def collect_remote_messages(lcpDescriptor_node, socket_visualizer, mac_address, label, request):
    """
    ****	SETUP Collect results funciton	****
    This functions is used to collect information from remote local control program,
    the statistics are sent to the experiment GUI, and stored in the node.measurements list
    """
    bad_plcp_old = 0
    good_plcp_old = 0
    bad_fcs_old = 0
    good_fcs_old = 0
    busy_time_old = 0

    interference_state = "NO interference"
    receive_thread = threading.currentThread()
    while getattr(receive_thread, "do_run", True):
        msg = lcpDescriptor_node.recv(timeout=0.1)
        if msg:
            # log.info("Recv: %s" % str(msg))
            if "mac_address" in msg:
                for ii in range(0, len(mac_address)):
                    if msg['mac_address'] == mac_address[ii]:
                        # print('message = %s - mac = %s' % (msg['measure'], msg['mac_address']))
                        msg['label'] = label[ii]
                        msg['type'] = u'statistics'

                        # print(msg)
                        socket_visualizer.send_json(msg)

            # add measurement on nodes element
            for node in wifinodes:
                if node.mac_address == msg['mac_address'] and msg['measure']:
                    node.measurements.append(msg['measure'])
        gevent.sleep(1)

def setAP(controller, node, iface, wlan_ip, essid):
    """ Creates infrastructure BSS, uses node such as Access Point
    :param node: elected Access Point Node
    :param essid: the SSID
    """
    # stop hostpad
    rvalue = controller.nodes(node).net.stop_hostapd()
    # set ip address
    rvalue = controller.nodes(node).net.set_ip_address(iface, wlan_ip)
    # set hostapd configuration
    rvalue = controller.nodes(node).net.set_hostapd_conf(iface, './helper/hostapd.conf', 6, essid)
    # start hostapd
    rvalue = controller.nodes(node).net.start_hostapd('./helper/hostapd.conf')
    # set power
    rvalue = controller.nodes(node).radio.set_tx_power(15)
    # set modulation rate
    rvalue = controller.nodes(node).radio.set_modulation_rate(6)

def setSTA(controller, node, iface, wlan_ip, essid):
    """ Associate node to infrastructure BSS
    :param node: elected station node by associate
    :param essid: the SSID
    """
    # stop hostpad
    rvalue = controller.nodes(node).net.stop_hostapd()
    # set ip address
    rvalue = controller.nodes(node).net.set_ip_address(iface, wlan_ip)
    # set power
    rvalue = controller.nodes(node).radio.set_tx_power(15)
    # set modulation rate
    rvalue = controller.nodes(node).radio.set_modulation_rate(6)
    connected = False
    for ii in range(10):
        # associate station
        rvalue = controller.nodes(node).net.connect_to_network(iface, essid)
        time.sleep(2)
        # dump connection
        rvalue = controller.nodes(node).net.network_dump(iface)
        # self.log.debug('dump connection :\n%s\n'  % (str(rvalue) ))
        flow_info_lines = rvalue.rstrip().split('\n')
        if flow_info_lines[0][0:9] == "Connected":
            connected = True
            break

    return connected

def set_hosts(host_file):
    hosts_info_file = open(host_file, 'r').readlines()
    hosts_info = []
    for i in hosts_info_file:
        if not i.startswith("#"):
            hosts_info.append(i)
    j = 0
    hosts = [i.split(',')[j] for i in hosts_info]
    j = j + 1
    driver = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    eth_ip = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    freq = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    tx_power = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    wlan_ip = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    mac_address = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    label = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    role = [i.split(',')[j].replace("\n", "") for i in hosts_info]
    j = j + 1
    iface = [i.split(',')[j].replace("\n", "") for i in hosts_info]

    return hosts, driver, eth_ip, freq, tx_power, wlan_ip, mac_address, label, role, iface


# Entry point after globals initialization
def main(args):
    global nodes
    global do_run

    # Init variables
    do_run = True

    # Init logging
    log.debug(args)
    log.info('****** 	WISHFUL  *****')
    log.info('****** Starting solution lte_ct ******')

    """
    ****** setup the communication with the solution global controller ******
    """
    # # Prepare our context in order to communicate with solution global controller
    # ctx = zmq.Context()
    # # Prepare our REQ/REP socket
    # request = ctx.socket(zmq.DEALER)
    # request.linger = 0
    # solution_global_controller = "127.0.0.1"
    # request.connect("tcp://" + solution_global_controller + ":7001")
    # # Prepare our SUBSCRIVER socket
    # subscriber = ctx.socket(zmq.SUB)
    # subscriber.linger = 0
    # subscriber.setsockopt(zmq.SUBSCRIBE, b'')
    # subscriber.connect("tcp://" + solution_global_controller + ":7000")
    #
    # # Register InterferenceDetection solution to global solution controller
    # request_result = register_solution_to_solution_global_controller(request)
    # if request_result:
    #     print("solution is correctly registered")
    # else:
    #     print("solution is not correctly registered")
    #     return False

    # # Start service for COMMAND/UPDATE from global solution controller
    # listener_subscriber_thread = threading.Thread(target=listener_subscriber, args=(0, subscriber))
    # listener_subscriber_thread.daemon = True
    # listener_subscriber_thread.start()


    """
    ****** Solution experiment controller ******
    """
    wlan_inject_iface = 'mon0'
    if args['--config']:
        config_file_path = args['--config']
        config = None
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
        controller.load_config(config)

    nodes_info_path = args['--nodes']
    if nodes_info_path:
        [hosts, driver, eth_ip, freq, tx_power, wlan_ip, mac_address, label, role, iface] = set_hosts(nodes_info_path)
        print([hosts, driver, eth_ip, freq, tx_power, wlan_ip, mac_address, label, role, iface])

    # Start controller
    controller.start()

    # control loop
    while do_run:
        gevent.sleep(1)
        print("\nConnected nodes", [str(node.id) for node in nodes])
        if len(nodes) >= len(hosts):
            time.sleep(1)
            lcpDescriptor_nodes = []
            reading_thread = []

            nodes_sort = []
            for ii in range(0, len(hosts)):
                for jj in range(0, len(nodes)):
                    if nodes[jj].ip == eth_ip[ii]:
                        nodes_sort.append(nodes[jj])

            print('sort nodes')
            for ii in range(0, len(nodes_sort)):
                print("\t %s - index %d" % (nodes_sort[ii].ip, ii))

            if len(nodes_sort) != len(hosts):
                print('Error in build node list')
                print('len(nodes_sort) != len(hosts) [%d != %d]' % (len(nodes_sort), len(hosts)))
                break
            else:
                print('len(nodes_sort) == len(hosts) [%d == %d]' % (len(nodes_sort), len(hosts)))

            nodes = nodes_sort

            time_update = 1  # seconds
            nodes_source_rate = []
            nodes_temp = []

            for ii in range(0, len(nodes)):
                nodes_source_rate.append(0)
                if not nodes[ii] in nodes_temp:
                    # print("node %s - index %d" % (nodes[ii].ip, ii) )
                    nodes_temp.append(nodes[ii])
            nodes = nodes_temp

            for ii in range(0, len(nodes)):
                wifinodes.append(WiFiNode(nodes[ii], mac_address[ii]))

            # START visualizer socket
            socket_visualizer = start_visualizer_connection()

            """
            ****** setup network ******
            """
            try:
                print("START nodes setup")
                all_nodes = ['A', 'B', 'C', 'D', 'E']

                # SETUP AP NODES
                for ii in range(0, len(hosts)):
                    # print("search node %s - index %d" % (eth_ip[ii], ii) )
                    for jj in range(0, len(nodes)):
                        if nodes[jj].ip == eth_ip[ii]:
                            pos = eth_ip.index(nodes[jj].ip)
                            if role[pos] == "AP":
                                print("setup topology node %s - index %d" % (nodes[jj].ip, jj))
                                setAP(controller, nodes[jj], iface[pos], wlan_ip[pos], "solution-lte-ct")
                            elif role[pos] == "MON":
                                pass
                            elif role[pos] == "STA":
                                pass
                            elif role[pos] == "EB":
                                print('\t- Starting program at TX Agent')
                                controller.node(nodes[jj]).radio.set_parameters({'IS_UE': False})
                                controller.node(nodes[jj]).radio.set_parameters({'FREQ': 2437000000})

                                # controller.node(nodes[0]).radio.set_parameters({'RF_AMP': 0.8})
                                controller.node(nodes[jj]).radio.set_parameters({'RF_AMP': 0.7})

                                # controller.node(nodes[0]).radio.set_parameters({'GAIN': 20})
                                controller.node(nodes[jj]).radio.set_parameters({'GAIN': 120})

                                # controller.node(nodes[1]).radio.set_parameters({'NO_OF_FRAMES': 100000})
                                controller.node(nodes[jj]).radio.set_parameters({'NO_OF_PRBS': 25})
                                controller.node(nodes[jj]).radio.set_parameters({'WHICH_PRBS': 0xFFFF})

                                # controller.node(nodes[0]).radio.set_parameters({'MCS': 1})
                                controller.node(nodes[jj]).radio.set_parameters({'MCS': 28})

                                # set any static  parameters needed to be set here for the ENB
                                # controller.node(nodes[jj]).radio.activate_radio_program('ENB')
                                # gevent.sleep(10)

                            else:
                                print("no station role found ")
                                break

                # SETUP STATIONS NODES
                for ii in range(0, len(hosts)):
                    print("search node %s - index %d" % (eth_ip[ii], ii))
                    for jj in range(0, len(nodes)):
                        if nodes[jj].ip == eth_ip[ii]:
                            pos = eth_ip.index(nodes[jj].ip)

                            # set up network nodes (ad-hoc)
                            # rvalue = controller.nodes(nodes[jj]).net.start_adhoc(driver[pos], "wlan0", "wishful-interference", freq[pos], tx_power[pos], "6", wlan_ip[pos], "250", "aa:bb:cc:dd:ee:ff", True)
                            # rvalue = controller.nodes(nodes[jj]).net.start_adhoc(driver[pos], "wlan0", "wishful-interference", freq[pos], tx_power[pos], "6", wlan_ip[pos], "off", "aa:bb:cc:dd:ee:ff", True)

                            # setup infrastructured network (put interface in managed mode and disable network manager)
                            # set up network nodes (infrastructured)
                            if role[pos] == "AP":
                                pass
                            elif role[pos] == "MON":
                                rvalue = controller.nodes(nodes[jj]).net.start_monitor(driver[pos], iface[pos])
                                rvalue = controller.nodes(nodes[jj]).radio.set_channel(iface[pos], "6")
                            elif role[pos] == "STA":
                                print("setup topology node %s - index %d" % (nodes[jj].ip, jj))
                                connection_result = setSTA(controller, nodes[jj], iface[pos], wlan_ip[pos], "solution-lte-ct")
                                print(connection_result)
                                if connection_result == False:
                                    raise SystemExit('Unable to connect')
                            else:
                                print("no station role found ")
                                break

                                # set up nodes monitor interface
                                # gevent.sleep(1)
                                # rvalue = controller.nodes(nodes[jj]).net.start_monitor(driver[pos], iface[pos])

                print("END node setup")
            except (Exception) as err:
                print("exception", err)
                print("Error in node setup procedure")
                do_run = False

            """
            ****** START LOCAL CONTROL PROGRAM ******
            """
            if do_run:
                try:
                    print("START local control program")
                    lcpDescriptor = None;
                    for ii in range(0, len(hosts)):
                        for jj in range(0, len(nodes)):
                            print("search node %s - index %d" % (eth_ip[ii], ii))
                            if nodes[jj].ip == eth_ip[ii]:
                                pos = eth_ip.index(nodes[jj].ip)
                                # if label[pos] == 'B' or label[pos] == 'C':
                                if True:
                                    # RUN local control program
                                    print("start local control program on nodes")
                                    lcpDescriptor_nodes.append(
                                        controller.node(nodes[jj]).hc.start_local_control_program(program=remote_control_program))
                                    msg = {"iface": iface[pos], "i_time": time_update}
                                    lcpDescriptor_nodes[ii].send(msg)
                                    print("start thread for collect measurements from nodes")
                                    # reading_thread.append(threading.Thread(target=collect_remote_messages, args=(lcpDescriptor_nodes[ii], socket_visualizer, mac_address, label, request)))
                                    reading_thread.append(threading.Thread(target=collect_remote_messages, args=(lcpDescriptor_nodes[ii], socket_visualizer, mac_address, label, 0)))
                                    reading_thread[ii].start()
                                break

                    print("END local control program setup")
                except (Exception) as err:
                    print("exception", err)
                    print("Error in node control program setup procedure")
                    do_run = False


                """
                ****** MAIN LOOP WITH interface commands management (start/stop iperf flows) ******
                """
                # sequence = 0
                # EXPERIMENT_DURATION = 15
                # dt = 0
                # monitorThrValue = 0
                # try:
                # 	while True:
                # 		monitorThrValue += 5
                # 		msg = {'type': 'monitorReport', 'monitorType': 'THR', 'monitorValue': monitorThrValue, 'monitorUnit': 'Mbps'}
                # 		print('msg %s' % str(msg))
                # 		sequence = 1
                # 		kvmsg = KVMsg(sequence)
                # 		kvmsg.key = b"generic"
                # 		kvmsg.body = json.dumps(msg).encode('utf-8')
                # 		kvmsg.send(request)
                # 		gevent.sleep(5)
                # 		dt += 1
                # 		if dt > EXPERIMENT_DURATION:
                # 			break
                # except KeyboardInterrupt:
                # 	return

                for jj in range(0, len(nodes)):
                    pos = eth_ip.index(nodes[jj].ip)
                    if label[pos] == 'B' or label[pos] == 'C':
                        controller.delay(1).nodes(nodes[jj]).net.create_packetflow_sink('1234', '1', True, 'wlan0')

                socket_command = start_command_connection()
                poller = zmq.Poller()
                poller.register(socket_command, flags=zmq.POLLIN)
                EXPERIMENT_DURATION = 30000000
                dt = 0
                while do_run:
                    socket_list = poller.poll(1000)
                    if socket_list:
                        for socket_info in socket_list:
                            if socket_info[1] == zmq.POLLIN:
                                parsed_json = socket_command.recv_json()
                                print('parsed_json : %s' % str(parsed_json))
                                type = parsed_json['type']

                                if type == 'traffic':
                                    node = parsed_json['src']
                                    node_src_index = all_nodes.index(node)
                                    command = parsed_json['command']
                                    nodes_source_rate[node_src_index] = 0
                                    if command == 'off_traffic':
                                        # if off traffic is selected for a specific node
                                        # call UPI to stop traffic on node
                                        controller.nodes(nodes[node_src_index]).net.stop_packetflow()
                                        if node == 'D':
                                            #off LTE network
                                            controller.node(nodes[node_src_index]).radio.deactivate_radio_program('ENB')
                                            pass
                                        else:
                                            pass

                                    # if start traffic is selected for a specific node
                                    if command == 'set_traffic':
                                        node = parsed_json['dst']
                                        node_dst_index = all_nodes.index(node)
                                        value = parsed_json['value']
                                        nodes_source_rate[node_src_index] = value
                                        source_rate = float(nodes_source_rate[node_src_index])
                                        # call UPI to start traffic
                                        if node == 'E':
                                            controller.node(nodes[node_src_index]).radio.activate_radio_program('ENB')
                                            gevent.sleep(5)
                                            # controller.delay(1).nodes(nodes[node_src_index]).net.start_packetflow("127.0.0.1", "2000", '3000', str(value), '1470')
                                        else:
                                            controller.delay(1).nodes(nodes[node_src_index]).net.start_packetflow(wlan_ip[node_dst_index], '1234', '3000', str(value) + 'K', '1470')

                    if not (dt % 10):
                        log.warning('waiting for ... (%d sec / %d)' % (dt, EXPERIMENT_DURATION))
                    dt += 1
                    gevent.sleep(1)
                    if dt > EXPERIMENT_DURATION:
                        break

            do_run = False
            for jj in range(0, len(nodes)):
                controller.nodes(nodes[jj]).net.stop_packetflow()

            for ii in range(0, len(nodes)):
                try:
                    controller.nodes(nodes[ii]).net.destroy_packetflow_sink()

                    if lcpDescriptor_nodes[ii]:
                        print("Terminate remote local control program")
                        lcpDescriptor_nodes[ii].close()

                    time.sleep(2)

                    print("Terminate receive thread")
                    reading_thread[ii].do_run = False
                    reading_thread[ii].join()
                except:
                    print('Error in %s local control program shutdown' % str(nodes[ii].ip))

            meas_collector.save_measurements(nodes=wifinodes, directory="experiment_data")


    # # We expect two agents (tx and rx).
    # # Observation: we dont check if the agents connectict are in fact the ones that we want.
    # while len(nodes) < TOTAL_NODES:
    #     print('-- Nodes connected: {}/{}'.format(len(nodes), TOTAL_NODES))
    #     gevent.sleep(2)
    #
    # print("All nodes connected. Starting Simple Experiment of wishful srs")
    #
    # running_enb = False
    # #running_enb = controller.node(nodes[0]).radio.get_running_radio_program()
    # if running_enb is False:
    #     print('\t- Starting program at TX Agent')
    #     controller.node(nodes[0]).radio.set_parameters({'IS_UE':False})
    #     controller.node(nodes[0]).radio.set_parameters({'FREQ': 2437000000})
    #
    #     # controller.node(nodes[0]).radio.set_parameters({'RF_AMP': 0.8})
    #     controller.node(nodes[0]).radio.set_parameters({'RF_AMP': 0.7})
    #
    #     # controller.node(nodes[0]).radio.set_parameters({'GAIN': 20})
    #     controller.node(nodes[0]).radio.set_parameters({'GAIN': 120})
    #
    #     #controller.node(nodes[1]).radio.set_parameters({'NO_OF_FRAMES': 100000})
    #     controller.node(nodes[0]).radio.set_parameters({'NO_OF_PRBS': 25})
    #     controller.node(nodes[0]).radio.set_parameters({'WHICH_PRBS': 0xFFFF})
    #
    #     # controller.node(nodes[0]).radio.set_parameters({'MCS': 1})
    #     controller.node(nodes[0]).radio.set_parameters({'MCS': 28})
    #
    #     # set any static  parameters needed to be set here for the ENB
    #     controller.node(nodes[0]).radio.activate_radio_program('ENB')
    # else:
    #     print('\t Agent TX is already running something. Please stop it first')
    #
    # # gevent.sleep(10)
    # # running_ue = False
    # # running_ue = controller.node(nodes[1]).radio.get_running_radio_program()
    # # if running_ue is False:
    # #     print('\t- Starting program at RX Agent')
    # #     # set any static  parameters needed to be set here for the UE
    # #     controller.node(nodes[1]).radio.set_parameters({'IS_UE':True})
    # #     controller.node(nodes[1]).radio.set_parameters({'FREQ': 2410000000})
    # #     controller.node(nodes[1]).radio.set_parameters({'GAIN': 30})
    # #     controller.node(nodes[1]).radio.set_parameters({'NO_OF_ANTENNAS': 1})
    # #     controller.node(nodes[1]).radio.set_parameters({'EQUALIZER_MODE': 'mmse'})
    # #     controller.node(nodes[1]).radio.set_parameters({'MAX_TURBO_ITS': 3})
    # #     controller.node(nodes[1]).radio.set_parameters({'NOISE_EST_ALG': 0})
    # #     controller.node(nodes[1]).radio.set_parameters({'MAX_TURBO_ITS': 3})
    # #     controller.node(nodes[1]).radio.set_parameters({'SSS_ALGORITHM': 1})
    # #     controller.node(nodes[1]).radio.set_parameters({'SNR_EMA_COEFF': 0.1})
    # #     controller.node(nodes[1]).radio.set_parameters({'CFO_TOL': 50})
    # #     #now that our parameters are set we can start our radio, these parameters have default values so they do not HAVE to be set
    # #     controller.node(nodes[0]).radio.activate_radio_program('UE')
    # # else:
    # #     print('\t Agent RX is already running something. Please stop it first')
    # # gevent.sleep(20)
    # # the following logic ensures the transmitter and receiver are on the same frequency
    # # vals = controller.node(nodes[0]).radio.get_parameters(['FREQ'])
    # # initial_cf_enb = vals['FREQ']
    # # if initial_cf_enb != initial_cf_ue:
    # #     controller.node(nodes[0]).radio.set_parameters({'FREQ': initial_cf_enb})
    # # gevent.sleep(10)
    # # meas = controller.node(nodes[0]).radio.get_measurements({'SNR'})
    # # snr = meas['SNR']
    # # print ('\t snr is \n', snr)
    # # gevent.sleep(2)
    # # if snr < 10:
    # #     controller.node(nodes[1]).radio.set_parameters({'GAIN': 20})
    # #
    # #
    # # gevent.sleep(5)
    # # meas  =  controller.node(nodes[0]).radio.get_measurements({'PDSCH_MISS'})
    # # pdsch_miss = meas['PDSCH_MISS']
    # # print ('\t pdsch_miss is \n',pdsch_miss)
    # # gevent.sleep(2)
    # # if pdsch_miss < 5:
    # #     param = controller.node(nodes[1]).radio.get_parameters(['MCS'])
    # #     mcs = param['MCS']
    # #     controller.node(nodes[1]).radio.set_parameters({'MCS': mcs + 2})
    # #
    # # gevent.sleep(30)
    # #
    # # meas = controller.node(nodes[0]).radio.get_measurements({'N_FRAMES'})
    # # n_frames = meas['N_FRAMES']
    # # print ('\t n_frames received  is \n', n_frames)
    # #
    # # controller.node(nodes[0]).radio.deactivate_radio_program('UE')
    # # controller.node(nodes[1]).radio.deactivate_radio_program('ENB')

    print('Controller Exiting')
    sys.exit()

if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    args = docopt(__doc__, version=__version__)
    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
        print('end main')
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
