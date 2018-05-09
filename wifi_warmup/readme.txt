Warm-up phase - Overlapping BSS Management
------------------------------------------

#Start AD WiSHFUL controller
python ../ad_controller/controller

#Start WiSHFUL controller
./controller --config ./configs/controller_config.yaml 

#Start AP0 WiSHFUL agent
./agent --config ./configs/ap0_config.yaml

#Start STA0 WiSHFUL agent
./agent --config ./configs/sta0_config.yaml

#Start AP1 WiSHFUL agent
./agent --config ./configs/ap1_config.yaml

#Start STA1 WiSHFUL agent
./agent --config ./configs/sta1_config.yaml
