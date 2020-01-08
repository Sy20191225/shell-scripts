#!/bin/bash
###
###
### 本脚本为合生科技推送项目配置文件使用；
###
###

HOSTS="/data/config/git_hosts"
CHK_SCRIPT='/srv/optool/ckconfig/check_config.sh'
[ ! -e ${CHK_SCRIPT} ] && echo 'Not found check config script' && exit 1

pro='0'
commitid='HEAD'
force=0

function usage() {
    cat <<EOF
[Usage]$0 -p project_name [-c commitid] [-f]
    -f force push
EOF
}

while [ ! -z "$1" ]
do
    case $1 in
        "-p")
            shift;
            pro="$1";
            truepro=`echo $pro|awk -F'_' '{print$NF}'`;;
         "-c")
             shift;
             commitid="$1";;
         "-f")
             shift;
             force=1;;
            *)
             usage;
             exit 1;;
      esac
      shift;
done

[[ $pro == '0' ]] && usage && exit 1

if [ ! -d /data/config/$pro ]
then
    echo "$pro is not a valid project, please reinput"
    exit 1
fi

cd /data/config/$pro

if [ ${commitid} == 'HEAD' ]
then
    git pull
    if [ $? -ne 0 ]
    then
       echo 'Git pull error'
       exit 2
    fi

    git add -A && git commit -m "update" >/dev/null 2>&1
    if [ $? -ne 0 ]
    then
        echo 'Noting to commit'
    else
        git push origin master
    fi

    real_commitid=`git log --format="%H" -1`
else
    real_commitid=${commitid}
    git pull && git revert ${real_commitid}..HEAD -n && git commit -m 'revert' && git push -f origin master  && echo 'Config has already reset'
    real_commitid=`git log --format="%H" -1`
fi

check_flag=1
for i in `find . -name "prod.properties"`
do
    ${CHK_SCRIPT} $i all | grep 'Failed' && echo -e "\033[31m ${pro}/${i} config check failed\033[0m"  && check_flag=0

done

if [ ${check_flag} -eq 1 ]
then
    echo -e '\033[0;32mConfig check success, push config...\033[0m'
elif [ ${force} -eq 1 ]
then
    echo -e '\033[0;32mConfig check failed, force push config...\033[0m'
else 
    exit 1
fi

/usr/bin/ansible $pro -m shell -a "cd /data/config/$truepro && git fetch && git checkout -m ${real_commitid}" -i ${HOSTS}
