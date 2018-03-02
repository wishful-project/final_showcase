Wishful INTERFERENCE
============================

### INTERFERENCE how-to on mobile testbed
 
### 1. run the showcase 
 #CONTROLLER
    nova
 
 #EXPERIMET NODES
    alix03,b43,10.8.8.103,2412,20,192.168.0.3,00:14:a5:e9:12:7c,A,MON,wlan0
    alix04,b43,10.8.8.104,2412,20,192.168.0.4,00:14:a5:e9:0c:74,B,AP,wlan0
    alix05,b43,10.8.8.105,2412,20,192.168.0.5,00:14:a4:62:c8:21,C,STA,wlan0

 #move files on ttilab
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.3:~/wishful-github-manifest-7/

    ...rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh clapton:~/wishful-github-manifest-7/
    ...ssh clapton "mkdir -p wishful-github-manifest-7/examples"
    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/
    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/helper
    ...rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/station-conf

 #connect to nodes
    ssh clapton.local

 #move on experiment directory
    cd wishful-github-manifest-4/final_showcase

 #sync clock nodes
    cd helper
    sh sync_date.sh root alix03,alix04,alix05
    sh sync_date.sh <user> clapton.local,nautilus.local,extensa.local

 #deploy directory on nodes
    sh deploy_upis.sh root alix03,alix04,alix05
    sh deploy_upis.sh <user> clapton.local,nautilus.local,extensa.local
    cd ..

 #Solution Global Controller
    (clapton)
    python3 ./controller

 #Solution
    (clapton)
    python3 controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_4hop.txt


    ~~~~
    #start agent
    ~~~~
    ssh clapton
    sudo python3 agent --config agent_cfg_sta_clapton.yaml
    ssh root@alix04
    python3 agent --config agent_cfg_sta.yaml
    ssh root@alix05
    python3 agent --config agent_cfg_sta.yaml
    ~~~~

    #controller (clapton --> CONTROLLER)
    ~~~~
    sudo python3 controller --config controller_cfg_clapton.yaml --nodes node_info_ttilab_3full.txt
    ~~~~

    #starting reading tool
    ~~~~
    cd wishful-github-manifest/final_showcase/solution_interference_detection/helper/
    ./b43-fwdump-ann
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

