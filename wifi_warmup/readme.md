Warm-up phase - Overlapping BSS Management
==========================================

0. Login as root to following nodes (passwd: root):

		ssh root@172.16.16.2
		ssh root@172.16.16.4
		ssh root@172.16.16.9
		ssh root@172.16.16.10

1. Start AD WiSHFUL controller on nuc9:

		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_ad.sh

2. Start WiSHFUL controller on nuc9:

		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_controller0.sh

3. Start AP0 WiSHFUL agent on nuc9:

		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_ap0.sh

4. Start STA0 WiSHFUL agent on nuc10:
		
		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_sta0.sh

5. Start WiSHFUL controller on nuc4:

		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_controller1.sh

6. Start AP1 WiSHFUL agent on nuc4:

		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scriptsts/start_ap1.sh

7. Start STA1 WiSHFUL agent on nuc2:
		
		/home/piotr/wifi_warmup/final_showcase/wifi_warmup/scripts/start_sta1.sh
