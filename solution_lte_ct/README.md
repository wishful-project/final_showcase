Wishful FINAL SHOWCASE solution_lte_ct
============================

### solution_lte_ct how-to on mobile showcase
 
### 1. run the showcase 
 #CONTROLLER
    nova
 
 #EXPERIMET NODES
    alix04,b43,10.8.8.104,2412,20,192.168.0.4,00:14:a5:e9:0c:74,B,AP,wlan0
    alix05,b43,10.8.8.105,2412,20,192.168.0.5,00:14:a4:62:c8:21,C,STA,wlan0
    nuc1,lte,10.8.9.13,2412,20,192.168.0.1,f4:4d:30:6c:63:a3,D,EB,eno1

 #move files on ttilab
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.3:~/wishful-github-manifest-7/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.13:~/wishful-github-manifest-7/


    ...rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh clapton:~/wishful-github-manifest-7/
    ...ssh clapton "mkdir -p wishful-github-manifest-7/examples"

    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/
    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/helper
    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/station-conf


 #connect to nodes
    ssh clapton.local

 #move on experiment directory
    cd wishful-github-manifest-7/final_showcase

    cd helper
     ex -sc $'%s/\r$//e|x' deploy_upis.sh
     ex -sc $'%s/\r$//e|x' sync_date.sh

 #sync clock nodes
    cd helper
    #sh sync_date.sh root alix03,alix04,alix05 # ,nuc1
    sh sync_date.sh root alix04,alix05 # ,nuc1
    sh sync_date.sh <user> clapton.local,nautilus.local,extensa.local

 #deploy directory on nodes
    #sh deploy_upis.sh root alix03,alix04,alix05
    sh deploy_upis.sh root alix04,alix05
    sh deploy_upis.sh <user> clapton.local,nautilus.local,extensa.local
    cd ..

 #Solution Global Controller
    python3 ./controller

 #Solution
    python3 controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_4hop.txt

    ~~~~
    #start agent
    ~~~~
    ssh clapton
    #sudo python3 agent --config agent_cfg_sta_clapton.yaml
    python3 agent --config agent_cfg_sta_mon.yaml
    ssh root@alix04
    python3 agent --config agent_cfg_sta.yaml
    ssh root@alix05
    python3 agent --config agent_cfg_sta.yaml
    ssh root@nuc1
    python3 agent_tx.py
    ~~~~

    #controller (nuc1 --> CONTROLLER)
    ~~~~
    #sudo python3 controller --config controller_cfg_clapton.yaml --nodes node_info_ttilab_3full.txt
    sudo python3 controller --config controller_cfg_nuc1.yaml --nodes node_info_ttilab_3full.txt
    ~~~~

    #starting reading tool
    ~~~~
    cd wishful-github-manifest-7/examples/interference_detection/station-conf/reading-tool/
    sudo ./b43-fwdump2
    ~~~~

~~~~
#start USRP
~~~~
ON USRP : http://10.8.8.22/login.html (ttilab)

ssh clapton
cd ~/work/usrp_acquire/python-usrp-tracker-v2/pyUsrpTracker
sudo sh run_usrp.sh 6
http://10.8.9.3/crewdemo/plots/usrp.png

ON ZIGBEE : http://10.8.8.22/login.html (ttilab)



Tunnel over ops:

~~~~
ssh -L 8601:10.11.16.39:8601 user@ops.wilab2.ilabt.iminds.be -v
ssh -L 8600:10.11.16.39:8600 user@ops.wilab2.ilabt.iminds.be -v
~~~~

#START graphical interface
cd visualizer
    python graphic_interface.py



### solution_lte_ct how-to on portable ttilab

 #deploy experiment files
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.13:~/wishful-github-manifest-7/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.3:~/wishful-github-manifest-7/
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh dgarlisi@172.16.16.10:/groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/
 #CONTROLLER
    nuc1

 #EXPERIMET NODES
    alix04,b43,10.8.8.104,2412,20,192.168.0.4,00:14:a5:e9:0c:74,B,AP,wlan0
    alix05,b43,10.8.8.105,2412,20,192.168.0.5,00:14:a4:62:c8:21,C,STA,wlan0
    nuc1,lte,10.8.9.13,2412,20,192.168.0.1,f4:4d:30:6c:63:a3,D,EB,eno1

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


Tunnel :
~~~~
putty on port 8500
~~~~
