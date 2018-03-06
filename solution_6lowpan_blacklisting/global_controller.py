#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_controller.py: Contiki global control program

Usage:
   global_controller.py [options] [-q | -v]

Options:
   --config configFile Config directory path

Example:
   python global_controller.py --config config/portable

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

__author__ = "Jan Bauwens & Peter Ruckebusch"
__copyright__ = "Copyright (c) ugent - idlab - imec"
__version__ = "0.1.0"
__email__ = "jan.bauwens2@ugent.be; peter.ruckebusch@ugent.be"

import datetime
import time
import logging
import gevent
import yaml
import sys

from contiki.contiki_helpers.global_node_manager import *
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *
from lib.global_controller_proxy import GlobalSolutionControllerProxy

## GLOBALS:
taisc_manager = None
app_manager = None
global_node_manager = None
wifi_to_tsch_channels_dct = {}

## CALLBACKS:
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

number_of_packets_received = 0
def macstats_event_cb(mac_address, event_name, event_value):
    if mac_address == 1:
        number_of_packets_received_cur = event_value[4]
        solutionCtrProxy.send_monitor_report("6lowpan-THR", (number_of_packets_received_cur - number_of_packets_received) * 128 * 8 / event_value[0], "Kbps")
        number_of_packets_received = number_of_packets_received_cur

## HELPER functions:
def mapWifiOnZigbeeChannels(log, channel_mapping):
    dct = {}
    try:
        file_n = open(channel_mapping, 'rt')
        import csv
        reader = csv.DictReader(file_n)
        for row in reader:
            dct[int(row["ieee80211"])] = []
            for x in row["ieee802154"].split('-'):
                dct[int(row["ieee80211"])].append(int(x))
    except Exception as e:
        logging.fatal("An error occurred while reading nodes: %s" % e)
    finally:
        file_n.close()
    return dct

blacklisted_channels = []
whitelisted_channels = []
## Commands implementation:
def blacklist():
    blacklisted_channels.append(wifi_to_tsch_channels_dct[6])
    logging.info("BLACKLIST {}".format(blacklisted_channels))

def whitelist():
    whitelisted_channels.append(wifi_to_tsch_channels_dct[6])
    logging.info("WHITELIST {}".format(whitelisted_channels))

def sicslowpan_start_application():
    server_nodes = [1]
    client_nodes = range(2,len(global_node_manager.get_mac_address_list())+1)
    logging.info("Activating server {}".format(server_node))
    app_manager.update_configuration({"app_activate": 1},server_nodes)
    logging.info("Activating clients {}".format(client_nodes))
    app_manager.update_configuration({"app_activate": 2},client_nodes)

def sicslowpan_stop_application():
    server_nodes = [1]
    client_nodes = range(2,len(global_node_manager.get_mac_address_list())+1)
    logging.info("Stopping server {}".format(server_node))
    app_manager.update_configuration({"app_activate": 0},server_nodes)
    logging.info("Stopping clients {}".format(client_nodes))
    app_manager.update_configuration({"app_activate": 0},client_nodes)

## MAIN functionality:
def main(args):
    # Init logging
    logging.debug(args)
    logging.info('****** 	WISHFUL  *****')
    logging.info('****** Starting solution (6lowpan_blacklisting) ******')

    """
    ****** setup the communication with the solution global controller ******
    """

    solutionCtrProxy = GlobalSolutionControllerProxy(ip_address="127.0.0.1", requestPort=7001, subPort=7000)
    solutionName = "6lowpan_blacklisting"
    commands = {
        "6LOWPAN_BLACKLIST": blacklist,
        "6LOWPAN_WHITELIST": whitelist,
        "6LOWPAN_START": sicslowpan_start_application,
        "6LOWPAN_STOP": sicslowpan_stop_application,
        }
    eventList = []
    monitorList = ["6lowpan-THR", "6lowpan-PER"]
    solutionCtrProxy.set_solution_attributes(solutionName, commands, eventList, monitorList )

    # Register 6lowpan_blacklisting solution to global solution controller
    response = solutionCtrProxy.register_solution()
    if response:
        logging.info("Solution was correctly registered to GlobalSolutionController")
        solutionCtrProxy.start_command_listener()
    else:
        logging.error("Solution was not registered to Global Solution Controller")

    # Update the TSCH configuration:
    contiki_nodes = global_node_manager.get_mac_address_list()
    logging.info("Connected nodes {}".format([str(node) for node in contiki_nodes]))
    
    taisc_manager.activate_radio_program("TSCH")
    taisc_manager.update_slotframe('taisc_slotframe.csv', 'TSCH')
    taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes)})
    
    logging.info("Finished configuring TSCH")
    
    while True:
        if len(whitelisted_channels):
            taisc_manager.whitelist_channels(whitelisted_channels)
            whitelisted_channels = []
        if len(blacklisted_channels):
            taisc_manager.blacklist_channels(blacklisted_channels)
            blacklisted_channels = []
        gevent.sleep(1)
    logging.info('Controller Exiting')
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
    
    # Logging:
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO  # default

    logfile = None
    if '--logfile' in args:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    # Set the paths:
    config_file_path = "{}/global_config.yaml".format(args['--config'])
    nodes_file_path = "{}/nodes.yaml".format(args['--config'])

    # Load the config file:
    global_controller_config = None
    with open(config_file_path, 'r') as file_handler:
        global_controller_config = yaml.load(file_handler)
    
    # Configure the node manager:
    global_node_manager = GlobalNodeManager(global_controller_config)
    global_node_manager.set_default_callback(default_callback)

    # Wait for all agents to connect to the global controller:
    with open(nodes_file_path, 'r') as file_handler:
        node_config = yaml.load(file_handler)
    global_node_manager.wait_for_agents(node_config['ip_address_list'])
    
    # Configure the helpers:   
    taisc_manager = TAISCMACManager(global_node_manager, "TDMA")
    app_manager = AppManager(global_node_manager)
    
    # Create blacklisting dict:
    wifi_to_tsch_channels_dct = mapWifiOnZigbeeChannels(logging, 'ieee80211_to_ieee802154_channels.csv')
    
    # Set the event callback:
    logging.info("Start local monitoring cp and events")
    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(1)
    taisc_manager.subscribe_events(["IEEE802154_event_macStats"], macstats_event_cb, 0)

    # Start MAIN functionality:
    try:
        main(args)
        print('End main')
    except KeyboardInterrupt:
        logging.debug("Controller exits")
    finally:
        logging.debug("Exit")
        global_node_manager.stop()
