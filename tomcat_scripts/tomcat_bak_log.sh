#!/bin/bash
###
###
### tomcat备份日志和清除日志脚本
###


date=`date +%Y_%m_%d`
old_7_date=$(date -d "7 days ago" +%Y%m%d)
bak_days=180
Reserved_days=5

tomcat_home_dir=/opt/link
bak_dir=/opt/link/lnjh_logs_bak

declare -a tomcat_info=(
    'channel tomcat-channel-8001'
    'manager tomcat-manager-13579'
    'task tomcat-task-8000'
)

for i in "${tomcat_info[@]}"; do

    line=($i)

    backlog() {

        mkdir -p $bak_dir/$1/$1-logs-"$old_7_date"

        find $tomcat_home_dir/$2/logs -type f -mtime +$Reserved_days -exec mv {} $bak_dir/$1/$1-logs-"$old_7_date" \;

        cd $bak_dir/$1
        tar -zcf $1-logs-"$old_7_date".tar.gz $1-logs-"$old_7_date"

        rm -rf $1-logs-"$old_7_date"

        find $bak_dir/$1 -type f -mtime +$bak_days -exec rm -f {} \;

        true > $tomcat_home_dir/$2/logs/catalina.out

    }

    backlog ${line[0]} ${line[1]}

done
