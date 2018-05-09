Wishful FINAL SHOWCASE Interference detection
============================

### network WiFi how-to on portable testbed

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
            python3 ./controller

    ssh dgarlisi@nuc11
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
               sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt


    ~~~~
    #start USRP channel trace visualizer on web portal
    ~~~~
    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
            sudo bash run_usrp.sh 6

    http://172.16.16.12/WishfulWebPortal/only_usrp.html
    
    
    
    #Start CNIT_MONITOR_SERVICE  (SHELL 4) (need AD controller activated):

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt
