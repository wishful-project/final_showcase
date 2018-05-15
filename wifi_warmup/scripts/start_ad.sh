DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*}
OBSS_PATH=${DIR%/*}

source $WISHFUL_PATH/dev/bin/activate
cd $AD_PATH
python ./controller
cd ..
