Wishful final showcase
============================

### how-to on w-ilab.t

### 0. Reserve and swap in the experiment
 EMULAB experiment link (atlas)
 https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=wishful
 
### 1. run the showcase 
 SOLUTION CONTROLLER

 EXPERIMET NODES
 #move files on wilab (we need copy one time, the wilab testbed filesystem replace all user directory on testbed nodes)
    cd final_showcase
    rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../  -e ssh 10.8.9.3:~/wishful-github-manifest-7/

 #connect to nodes
  ssh user@ops.wilab2.ilabt.iminds.be
  ssh user@zotacd6
  ...
  ssh user@zotach4

 #move on experiment directory
  cd wishful-github-manifest-

 #sync clock nodes
  sh sync_date.sh user zotacc6,zotacg6,zotack6,zotacb1,zotack1,zotaci3.....

 #start agent
  sudo python3 agent --config agent_cfg_wilab.yaml.....

 #controller (zotach4 (39) --> CONTROLLER)
 sudo python3 controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_4hop.txt


### start USRP
ON USRP :
ssh
    ssh
        sudo sh run_usrp.sh 6


### START graphical interface
on local pc
    python3 graphic_interface.py

