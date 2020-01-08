#! /bin/bash
###
###
### 本脚本为配置文件校验脚本；
###
###

a=$(echo $0)
path=$1
command_path=$(dirname ${0})
if [ "x${path}" == "x" ];then
    type="help"
else
    type=${2-all}
fi

if [ ! -f ${path} ];then
    echo "${path} not is exitst!"
    exit 1
fi

for script in $(echo mysql_config_check.py redis_check.py zookeeper_check.py)
do
    if [ ! -x ${command_path}/$script ];then
        echo "${command_path}/$script not exec script please chmod +x ${command_path}/$script"
        exit 1
    fi
done

case ${type} in
    mysql)
        ${command_path}/mysql_config_check.py --path ${path}
        ;;
    redis)
       ${command_path}/redis_check.py --path ${path}
       ;;
    zookeeper) 
        ${command_path}/zookeeper_check.py --path ${path}
        ;;
    rabbitmq)
        ${command_path}/rabbitmq_check.py --path ${path}
    ;;
     all)
         echo "check mysql config"
         ${command_path}/mysql_config_check.py --path ${path}
         echo "check redis config"
         ${command_path}/redis_check.py --path ${path}
         echo "check zookeeper config"
         ${command_path}/zookeeper_check.py --path ${path}
         echo "check rabbitmq config"
         ${command_path}/rabbitmq_check.py --path ${path}
         ;;
       help)
           echo "Usage $0  config_path_file {mysql|redis|rabbitmq|zookeeper|all}"
           ;;
esac
