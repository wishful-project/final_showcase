Wishful final showcase
============================

### Showcase Phases

Only 1 Administrative Domain present with multiple Wi-Fi deployments to enable the use of the Wi-Fi air time management type of showcases if needed. TUB.e
    Phase 1: LTE added as interferer, CNIT.d (if blank subframes are enabled) , TUB.b, IMEC.a
    Phase 2: (LTE WiSHFUL enabled added, LTE interferer removed) LTE added in 1st AD. (LTE-WIFI coexistence)  TUB.d , CNIT.d, (if collaboration challenge exist)
Phase 3: ADD 2nd Second AD.
    First AD IMEC ZB, 2nd AD TCD virtualized OFDM based networks (frequency separation ? cooperation on the 2.4 GHz band,  blacklisting) IMEC.a, TCD.b

link

### Showcase Architecture

The repository is organized with a different directory for each solution, moreover there are three additional directories, solution_global controller, showcase_GUI and lib.


### How work the solution global controller

The paradigm of communication between a generic solution and the solution global controller has two different phases.
    Phase 1: The solutions use a request/reply format to register them on solution global controller ( the following information
    are required for the registration procedure: Name; monitorList; commandList; eventList;).
    Phase 2: The solutions use a request/reply format to send monitor information and event detected to the solution global controller.
    The solution global controller uses the PUB/SUB to send command to the solutions.

The solutions are registered in the solutionCompatibilityMatrix map, we add also eventually conflict between the solutions in order to
use this information in the main logic of the solution global controller. The main logic of the solution global controller waiting for
receiving a monitor/event report, the solution global controller checks the solution compatibility matrix, in order to understand eventually conflict,
and send update/command to solutions. Example: when it receives the report of detecting interference (LTE),
sends activation command to solution TDMA cross interference, if not conflict are detected.

link

### how-to showcase activation on w-ilab.t

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


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).