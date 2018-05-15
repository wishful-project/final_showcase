DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*}
OBSS_PATH=${DIR%/*}

# start python virtual env
source $WISHFUL_PATH/dev/bin/activate
cd $OBSS_PATH
./controller --config ./configs/controller0_config.yaml
cd ..
