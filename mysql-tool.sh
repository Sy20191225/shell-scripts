#!/bin/bash

#######################################################
# 名字：       mysql-tool.sh
# 版本：       v1.0
# 作者：       sy
# 功能：       MySQL 数据库管理工具
# 创建日期：    2019-09-23
# 备注：       此脚本为合生科技 MySQL 数据管理使用
#######################################################

export MYSQL_PWD="*******************"
shell_dir=$(cd "$(dirname "$0")";pwd)

bin_dir="/srv/mysql3306/bin/mysql"
user="root"
port="3306"
host="192.168.%.%"
db_conn="${bin_dir} -u${user} -P${port}"


log(){
    local text;local logtype;local time
    time=$(date +'%F %H:%M:%S')
    logfile=${shell_dir}/mysql-tool.log
    logtype=$1
    text=$2
    case $logtype in 
        error)
            #echo -e "\033[31m`date +'%F %H:%M:%S'`\t${logtype}\t${text}\033[0m" | tee -a ${logfile};;
            echo -e "\033[31m${text}\033[0m"
            echo -e "\033[31m${time}\t${logtype}\t${text}\033[0m" >> ${logfile};;
        info)
            #echo -e "\033[32m`date +'%F %H:%M:%S'`\t${logtype}\t${text}\033[0m" | tee -a ${logfile};;
            echo -e "\033[32m${text}\033[0m"
            echo -e "\033[32m${time}\t${logtype}\t${text}\033[0m" >> ${logfile};;
        warn)
            #echo -e "\033[33m`date +'%F %H:%M:%S'`\t${logtype}\t${text}\033[0m" | tee -a ${logfile};;
            echo -e "\033[33m${text}\033[0m"
            echo -e "\033[33m${time}\t${logtype}\t${text}\033[0m" >> ${logfile};;
    esac
}

flush(){
    ${db_conn} -e "flush privileges;"
}

auth_user_presence(){
    local select_user="select user from mysql.user;"
    name=$(${db_conn} -e "${select_user}" | grep -o -E -w "$1")
    if [ $? -eq 0 ];then
        return 0
    else
        return 1
    fi
}

auth_database(){
    local sel_data="show databases;"
    data_name=$(${db_conn} -e "${sel_data}" | grep -o -E -w "$1")
    if [ $? -eq 0 ];then
        return 0
    else
        return 1
    fi
}

auth_database_no(){
    local i=0
    while (( i < 3 ))
    do
        let "i += 1";
        read -p "请输入数据库名称( $i or 3 ):" database
        if [ -z "$database" ]
        then
            log warn "输入数据库名称不能为NULL,请重新输入"
            continue
        fi
        auth_database ${database};
        if [ $? -eq 1 ];then
            log warn "数据库 $database 不存在,请重新输入"
            continue
        fi
        let "i -= 1";
        break
    done
    if [ "$i" -ge 3 ];then
        log warn "您已输入 $i 次,验证失败,返回菜单"
        continue
    fi
}

user_info(){
    log info "查询数据库所有用户的信息"
    local select_users="select user,host from mysql.user where host = '${host}';"
    ${db_conn} -e "${select_users}"
}

auth_user_no(){
    local i=0
    while (( i < 3 ))
    do
        let "i += 1";
        read -p "请输入用户名( $i or 3 ):" username
        if [ -z "$username" ]
        then
            log warn "您输入的用户名不能为NULL,请重新输入"
            continue
        fi
        auth_user_presence ${username};
        if [ $? -eq 1 ];then
            log warn "您输入的用户名不存在,请重新输入"
            continue
        fi
        let "i -= 1";
        break
    done
    if [ "$i" -ge 3 ];then
        log warn "您已输入 $i 次,验证失败,返回菜单"
        continue
    fi
}

create_user(){
    log info "正在创建用户信息"
    local i=0
    while (( i < 3 ))
    do
        let "i += 1";
        read -p "请输入用户名( $i or 3 ):" username
        if [ -z "$username" ]
        then
            log warn "您输入的用户名不能为NULL,请重新输入"
            continue
        fi
        auth_user_presence ${username};
        if [ $? -eq 0 ];then
            log warn "您输入的用户名不存在,请重新输入"
            continue
        fi
        let "i -= 1";
        break
    done
    if [ "$i" -ge 3 ];then
        log warn "您已输入 $i 次,验证失败,返回菜单"
        continue
    fi
    
    local a=0
    while (( a < 3 ))
    do
        read -p "请输入密码( $a or 3 ):" password
        read -p "请再次输入密码( $a or 3 ):" retypepassword
        if [ -z "$password" ]; then
            log warn "您输入的密码不能为NULL,请重新输入"
            continue
        fi
        if [ "x$password" != "x$retypepassword" ]; then
            log warn "两次输入的密码不相同,请重新输入"
            continue
        fi
        let "a -= 1";
        break
    done
    if [ "$a" -ge 3 ];then
        log warn "您已输入 $a 次,验证失败,返回菜单"
        continue
    fi
    local createuser="create user '${username}'@'${host}' identified by '${password}';"
    ${db_conn} -e "${createuser}"
    flush;
    log info "添加用户成功,用户名：${username} 密码：${password}"
}

pwd_update(){
    log info "正在修改用户密码"
    auth_user_no;

    local a=0
    while (( a < 3 ))
    do
        read -p "请输入新的密码( $a or 3 ):" password
        read -p "请重新输入密码( $a or 3 ):" retypepassword
        if [ -z "$password" ]; then
            log warn "您输入的密码不能为NULL,请重新输入"
            continue
        fi
        if [ "x$password" != "x$retypepassword" ]; then
            log warn "两次输入的密码不相同,请重新输入"
            continue
        fi
        let "a -= 1";
        break
    done
    if [ "$a" -ge 3 ];then
        log warn "您已输入 $a 次,验证失败,返回菜单"
        continue
    fi
    local update_pwd="update mysql.user set authentication_string=password('${password}') where user='${username}';"
    ${db_conn} -e "${update_pwd}"
    flush;
    log info "用户密码修改成功,用户名：${username} 新密码：${password}"
}

drop_user(){
    log info "正在删除用户信息"
    auth_user_no;
    local user_drop="drop user '${username}'@'${host}';"
    ${db_conn} -e "${user_drop}"
    flush
    log info "删除用户 ${username} 成功"
}

re_enter(){
    log warn "对不起,不识别您输入的序号 $1 ,请重新输入"
}

add_grant(){
    log info "正在增加用户权限信息"
    auth_user_no;
    auth_database_no;
    read -p "请输入增加的权限(用逗号隔开,如:select,insert,update,delete,create,alter,drop):" grants
    local add_user_grant="grant ${grants} on ${database}.* to '${username}'@'${host}';"
    ${db_conn} -e "${add_user_grant}"
    flush
}

sel_grant(){
    log info "正在查询用户权限信息"
    auth_user_no;
    local sel_user_grant="show grants for '${username}'@'${host}';"
    ${db_conn} -e "${sel_user_grant}"
}

remove_grant(){
    log info "正在移除用户权限信息"
    auth_user_no;
    auth_database_no;
    read -p "请输入移除的权限(用逗号隔开,如:select,insert,update,delete,create,alter,drop):" grants
    local rev_user_grant="revoke ${grants} on ${database}.* from '${username}'@'${host}';"
    ${db_conn} -e "${rev_user_grant}"
    flush
}

database_info(){
    local show_database="show databases;"
    ${db_conn} -e "${show_database}"
}

usage(){
    case $choice in
        1)
            while :
            do
                echo -e "\033[33m请选择操作项序号：\033[0m"
                echo -e "\033[36m                 1 添加用户 \033[0m"
                echo -e "\033[36m                 2 修改用户密码 \033[0m"
                echo -e "\033[36m                 3 删除用户 \033[0m"
                echo -e "\033[36m                 4 查询所有用户信息 \033[0m"
                echo -e "\033[36m                 0 返回主菜单 \033[0m"
                echo -e "\033[36m                 9 退出脚本 \033[0m"
                echo ""
                read -p "请输入:" YES_OR_NO

                if [ "$YES_OR_NO" = "1" ]; then
                    create_user;
                    continue
                elif [ "$YES_OR_NO" = "2" ]; then
                    pwd_update;
                    continue
                elif [ "$YES_OR_NO" = "3" ]; then
                    drop_user;
                    continue
                elif [ "$YES_OR_NO" = "4" ]; then
                    user_info;
                    continue
                elif [ "$YES_OR_NO" = "0" ]; then
                    log info "返回主菜单"
                    echo " "
                    break
                elif [ "$YES_OR_NO" = "9" ]; then
                    log info "*******即将退出本程序*******"
                    exit 0
                else
                    re_enter $YES_OR_NO;
                fi
            done
            ;;

        2)
            while :
            do
                echo -e "\033[33m请选择操作项序号：\033[0m"
                echo -e "\033[36m                 1 查询用户权限 \033[0m"
                echo -e "\033[36m                 2 增加用户权限 \033[0m"
                echo -e "\033[36m                 3 移除用户权限 \033[0m"
                echo -e "\033[36m                 4 数据库信息 \033[0m"
                echo -e "\033[36m                 0 返回主菜单 \033[0m"
                echo -e "\033[36m                 9 退出脚本 \033[0m"
                echo ""
                read -p "请输入:" YES_OR_NO

                if [ "$YES_OR_NO" = "1" ]; then
                    sel_grant;
                    continue

                elif [ "$YES_OR_NO" = "2" ]; then
                    add_grant;
                    continue

                elif [ "$YES_OR_NO" = "3" ]; then
                    remove_grant;
                    continue

                elif [ "$YES_OR_NO" = "4" ]; then
                    database_info;
                    continue

                elif [ "$YES_OR_NO" = "0" ]; then
                    log info "*******返回主菜单*******"
                    echo " "
                    break

                elif [ "$YES_OR_NO" = "9" ]; then
                    log info "*******即将退出本程序*******"
                    exit 0

                else
                    re_enter $YES_OR_NO;
                fi
            done
            ;;

        0)
            log info "*******即将退出本程序*******"
            exit 0
            ;;

        *)
            echo -e "\033[33m对不起,不能识别您输入的序号 ${choice} ,请重新输入.\033[0m"
            ;;

    esac
}
while :
do
cat<<EOF
        ******************************************************************************************

                                                MySQL管理工具 

        ******************************************************************************************
                           按 1 用户管理:
                                          添加用户,修改用户密码,删除用户,查询所有用户信息
                           按 2 权限管理:
                                          查询用户权限,增加用户权限,移除用户权限,数据库信息
                           按 0 退出脚本

        ******************************************************************************************
EOF
    read -p "请输入你的选择:" choice
    usage
done