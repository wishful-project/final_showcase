WISHFUL_PATH=/root/final_showcase
OBSS_PATH=$WISHFUL_PATH/final_showcase/wifi_warmup

source $WISHFUL_PATH/dev/bin/activate
cd $OBSS_PATH
./controller --config ./configs/controller0_config.yaml
cd ..
