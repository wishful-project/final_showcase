Wishful FINAL SHOWCASE solution_lte_ct
============================

### network_lte how-to on portable testbed

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
            python3 ./controller

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct/
            ex -sc $"%s/\r$//e|x" start_lte_network.sh
            bash start_lte_network.sh

~~~~
#start USRP channel trace visualizer on web portal
~~~~

    ssh dgarlisi@nuc12
        cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
            sudo bash run_usrp.sh 6

    http://172.16.16.12/WishfulWebPortal/only_usrp.html


 ## run separated command

 #deploy experiment files
    cd /mnt/d/ownCloud/wishful-framework-cnit/wishful-github-manifest-7/final_showcase/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.11:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/

 #CONTROLLER
    nuc12

 #EXPERIMET NODES
    nuc11,lte,172.16.16.11,2412,20,192.168.0.1,f4:4d:30:6c:63:a3,D,EB,eth0

 #deploy directory on nodes
 #sync clock nodes
    cd helper
     ex -sc $'%s/\r$//e|x' sync_date.sh
     sh sync_date.sh root alix04,alix05  #sync nodes time
     cd ..

 #Solution Global Controller
    python3 ./controller

 #Solution
    python3 controller --config controller_cfg_clapton.yaml --nodes node_info_ttilab_3full.txt
    python3 controller --config controller_cfg_nuc12.yaml --nodes node_info_ttilab_3full.txt
    python3 controller --config controller_cfg_nuc10.yaml --nodes node_info_ttilab_3full.txt

    ~~~~
    #start agent
    ~~~~
    ssh root@alix03
    python3 agent --config agent_cfg_sta_mon.yaml
    ssh root@alix04
    python3 agent --config agent_cfg_ap.yaml
    ssh root@alix05
    python3 agent --config agent_cfg_sta.yaml
    ssh nuc1
    python3 agent_tx.py
    ~~~~

 #Start LTE traffic
    iperf -c 127.0.0.1 -p 2000 -i 1 -t 10000

 #Change LTE pattern
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct
    python3 set_tx_lte_pattern.py -w 1010101010




