DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*/*}
DET_PATH=$WISHFUL_PATH/final_showcase/spectrum_monitoring_service/solution_interference_classifier

source $WISHFUL_PATH/dev/bin/activate
cd $DET_PATH
./lte_u_bs_controller --config ./configs/lte_u_bs_config.yaml
cd ..
