#!/bin/bash

#if [ $# -lt 1 ]; then
#	echo "usage $0 <user> <nodes_list> (use ',' to separate nodes in list )"
#	exit
#fi

set -x

#     cd helper
#     ex -sc $"%s/\r$//e|x" sync_date.sh
#     sh sync_date.sh dgarlisi nuc11  #sync nodes time
#     cd ..

    ssh dgarlisi@nuc11 "cd ~/wishful-github-manifest/final_showcase/network_lte/solution_lte_ct && python3 agent_tx.py > agent.out 2> agent.err < /dev/null &" &
    sleep 2
    python3 controller --config controller_cfg_nuc12.yaml --nodes node_info_ttilab_3full.txt

set +x


