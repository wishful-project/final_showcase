Wishful FINAL SHOWCASE solution_lte_ct
============================

### network_lte how-to on mobile showcase
 
 #deploy experiment files
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.10:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/

 #CONTROLLER
    nuc12

 #EXPERIMET NODES
    nuc11,lte,172.16.16.11,2412,20,192.168.0.1,f4:4d:30:6c:63:a3,D,EB,eth0

 #deploy directory on nodes
 #sync clock nodes
    cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     sh deploy_upis.sh root alix04,alix05  #deploy framework on alixnodes
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
    python set_tx_lte_pattern.py -w "1,0,0,1,1,1,1,1,0,0"
        ('UDP target IP:', '127.0.0.1')
        ('UDP target port:', 8888)
        1,0,0,1,1,1,1,1,0,0


~~~~
#start USRP
~~~~

ssh clapton
cd ~/work/usrp_acquire/python-usrp-tracker-v2/pyUsrpTracker
sudo sh run_usrp.sh 6
http://10.8.9.3/crewdemo/plots/usrp.png

ON ZIGBEE : http://10.8.8.22/login.html (ttilab)


