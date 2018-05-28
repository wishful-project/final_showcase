WiPLUS - LTE-U detector
==========================================

0. Login as root to following nodes (passwd: root):

		ssh root@172.16.16.1
		ssh root@172.16.16.2

1. Start WiPLUS detector controller on nuc1:

		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_lte_u_bs.sh 172.16.16.9

2. Start LTE-U BS controller on nuc2:

		/home/piotr/wishful/final_showcase/spectrum_monitoring_service/solution_interference_classifier/scripts/start_wiplus.sh 172.16.16.9

3. Commands for LTE-U BS:

* ACTIVATE - start srsLTE LTE-U BS, center frequency can be given as arg, default is 2412MHz (i.e. WiFI channel 1)
* DEACTIVATE - stop srsLTE LTE-U BS
* SET_FREQ - change center frequency of LTE-U BS
