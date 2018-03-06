Wishful FINAL SHOWCASE solution_6lowpan_blacklisting
By Jan Bauwens (imec)
============================

### solution_6lowpan_blacklisting how-to

### 0. Flash the sensor nodes:
# Navigate to the udp example directory:
cd ~/contiki/examples/wishful-ipv6/taisc/udp/
# Execute the make command (X is the node id)
make TARGET=zoul udp-example.upload NODE_ID=X MOTES=/dev/ttyUSB0

### 1. run the agent:
# Activate the virtual environment:
source ./dev/bin/activate
# Go to the 6lowpan blacklisting solution
cd final_showcase/solution_6lowpan_blacklisting
# Start the agent:
# - Single node per agent, connection to global controller via eth0 interface
python agent --config agent_config_eth0.yaml 
# - Three nodes per agent, connection to global controller via lo interface
python agent --config agent_config_eth0.yaml 
    
### 2. run the global controller:
# Activate the virtual environment:
source ./dev/bin/activate
# Go to the 6lowpan blacklisting solution
cd final_showcase/solution_6lowpan_blacklisting
# Start the global controller:
python 
