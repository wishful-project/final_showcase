#start Solution Interference Classifier controller
#start with -v for debugging
cd ../solution_global_controller/
python3 ./controller

#start Solution Interference Classifier controller
#start with -v for debugging
./wishful_controller --config ./controller_config.yaml

#start WiPLUS agent
#start with -v for debugging
./wishful_agent --config ./wiplus_agent_config.yaml
