Warm-up phase - Overlapping BSS Management
------------------------------------------

# Go to WiFi Warm-up phase
cd /final_showcase/wifi_warmup/scripts/

#Start AD WiSHFUL controller
./start_ad.sh

#Start WiSHFUL controller
./start_controller0.sh

#Start AP0 WiSHFUL agent
./start_ap0.sh

#Start STA0 WiSHFUL agent
./start_sta0.sh

#Start WiSHFUL controller
./start_controller1.sh

#Start AP1 WiSHFUL agent
./start_ap1.sh

#Start STA1 WiSHFUL agent
./start_sta1.sh
