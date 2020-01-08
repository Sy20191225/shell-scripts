#!/bin/sh
###
###
###

S_PATH="$1"
FILE="$2"
D_PATH="$3"
USER="$4"
PWD="$5"

#ftp server IP.
FTP_IP="0.0.0.0"

usage() {
    cat <<EOF
脚本实用说明：
usage: $(basename $0) "S_PATH" "FILE" "D_PATH" "USER" "PWD"

      S_PATH：FTP服务端文件目录；
      FILE：下载的文件名；
      D_PATH：本地保存文件目录，默认为当前执行脚本的目录；
      USER：FTP用户名，输入空后需手动输入；
      PWD：FTP密码，输入空后需手动输入；
EOF
}

#验证服务端目录
is_spath() {
    [ -z "${S_PATH}" ] && return 0
    return 1
}
is_spath && { usage; echo "FTP服务路径为空"; exit 1; }

#验证服务端文件
is_file() {
    [ -z "${FILE}" ] && return 0
    return 1
}
is_file && { usage; echo "文件名为空"; exit 1; }

#验证本地目录
is_dpath() {
    [ -z "${D_PATH}" ] && return 0
    return 1
}
is_dpath && { D_PATH="$(pwd)"; echo "本地下载路径输入为空，默认为当前目录\"$D_PATH\"";}

if [ ! -d "${D_PATH}" ]; then
    echo "目录 ${D_PATH} 不存在；"
    exit 1;
fi;

#输入用户
auth_user() {
    local i=0
    while (( i < 3 ))
    do
        let "i += 1";
        read -p "请输入FTP用户名( $i or 3 ):" USER
        if [ -z "$USER" ]
        then
            echo "FTP用户名不能为NULL,请重新输入"
            continue
        fi;
        let "i -= 1";
        break
	done
    if [ "$i" -ge 3 ];then
        echo "已输入 $i 次,验证失败,退出"
        exit 1;
    fi;
}

#输入密码
auth_pwd() {
    local i=0
    while (( i < 3 ))
    do
        let "i += 1";
        read -p "请输入FTP用户密码( $i or 3 ):" -s PWD
        if [ -z "$PWD" ]
        then
            echo "FTP用户密码不能为NULL,请重新输入"
            continue
        fi;
        let "i -= 1";
        break
	done
    if [ "$i" -ge 3 ];then
        echo "已输入 $i 次,验证失败,退出"
        exit 1;
    fi;
}

#验证用户
is_user() {
    [ -z "${USER}" ] && return 0
    return 1
}
is_user && { auth_user; }

#验证密码
is_pwd() {
    [ -z "${PWD}" ] && return 0
    return 1
}
is_pwd && { auth_pwd; }


#ftp操作
ftp_dw() {
    ftp -v -n ${FTP_IP}<<EOF
user ${USER} ${PWD}
binary
cd ${S_PATH}
lcd ${D_PATH}
prompt
get ${FILE}
bye
EOF
}

#验证文件是否更新
fun_check_stat_file(){
    CHECK_STAT_FILE="$1";
    CHECK_INTERVAL="${2:-120}";

    if [ ! -f ${CHECK_STAT_FILE} ] ;then
        echo -1;
        return;
    fi;

    FILE_MODIFY_TIME="`stat ${CHECK_STAT_FILE}|egrep '最近更改|Modify'|awk -F'[： ]' '{print $2" "substr($3,1,8);}'`";
    FILE_MODIFY_TIME_SECONDS="`date -d "${FILE_MODIFY_TIME}" +%s`";
    CURRENT_TIME_SECONDS="`date +%s`";

    if [ `expr ${CURRENT_TIME_SECONDS} - ${FILE_MODIFY_TIME_SECONDS}` -lt  ${CHECK_INTERVAL} ] ;then
        echo 1;
        return;
    else
        echo 0;
        return;
    fi;
}

#验证系统ftp服务
ftp_num=$(rpm -qa|grep -w ftp|wc -l)
if [ ${ftp_num} -eq 0 ]; then
    yum install -y ftp >/dev/null 2>&1
fi;

ftp_dw
DIR_FILE="${D_PATH}/${FILE}"

if [ -e "${DIR_FILE}" ]; then
    CHECK_STAT_FILE_FLAG=`fun_check_stat_file ${DIR_FILE} 60`;
    if [ ${CHECK_STAT_FILE_FLAG} -ne 1 ] ;then
        echo "文件 ${FILE} 没有更新."
        exit;
    fi;
    echo "下载文件 ${FILE} 成功."
fi;
