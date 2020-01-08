#! /srv/python2/bin/python
#! -*- coding:utf8 -*-

import mysql.connector
import sys
import os
import re
import argparse
from prettytable import PrettyTable



class Echo:
    def __init__(self):
        self.obj = PrettyTable(['host', 'port', 'user', 'password', 'database', 'is_table', 'status', 'error info'])
    
    def make_echo(self, data):
        self.obj.add_row(self.__format(data))

    def echo(self):
        print self.obj

    def __format(self, data):
        if data[-2] == 'Waring':
            data[-2] = '\033[1;33mWaring\033[0m'
            data[-1] = '\033[1;33m{}\033[0m'.format(data[-1])
        elif data[-2] == 'Failed':
            data[-2] = '\033[1;31mFailed\033[0m'
            data[-1] = '\033[1;31m{}\033[0m'.format(data[-1])
        elif data[-2] == 'Success':
            data[-2] = '\033[1;32mSuccess\033[0m'
        else:
            data[-2] = '\033[1;34m{}\033[0m'.format(data[-2])

        return data



def read(filename):
    with open(filename) as f:
        return f.readlines()


def get_config(data):
    jdbc_list = []
    jdbc_url_is = False
    jdbc_uesr_is = False
    jdbc_password_is = False
    for x in data:
        if not re.match('^jdbc', x.strip()):
            continue
        if re.match(r'^jdbc.\S+.url', x.strip()):
            url_match = re.search('^jdbc.(\S+).url=(.*)', x.strip())
            tmp_jdbc_url = url_match.group(2)
            key_name = url_match.group(1)
            jdbc_url_is = True
        elif re.match(r'^jdbc.\S+.user', x.strip()):
            user_match = re.search('^jdbc.\S+.user.*=(.*)', x.strip())
            tmp_user = user_match.group(1)
            jdbc_uesr_is = True

        elif re.match(r'^jdbc.\S+.password', x.strip()):
            password_match = re.search('^jdbc.\S+.password=(.*)', x.strip())
            tmp_password = password_match.group(1)
            jdbc_password_is = True
        if jdbc_url_is and jdbc_uesr_is  and jdbc_password_is:
            jdbc_list.append({
                '{}'.format(key_name):{
                    'url': tmp_jdbc_url,
                    'user': tmp_user,
                    'password': tmp_password
                    }
                })
            jdbc_url_is = jdbc_uesr_is = jdbc_password_is = False
    return jdbc_list        


def match_url(url):
    match_data = re.search(r'jdbc:mysql://(\S+)/(\S+)\?', url)
    if match_data is None:
        return {"host": "localhost", "port": 3306, "database": "test"}
    tmp_host = match_data.group(1).split(':')
    if len(tmp_host) == 1:
        port = '3306'
    else:
        port = tmp_host[1]
    host = tmp_host[0]
    database = match_data.group(2)
    return {'host': host,'port': port, 'database': database}

def format_config(data):
    url_list = data['url'].split(',')
    password = data['password'].split(',')
    user = data['user'].split(',')
    config = list()
    for url in url_list:
        data = match_url(url)
        try:
            now_password = password[url_list.index(url)]
        except IndexError:
            now_password = ''
        try:
            now_user = user[url_list.index(url)]
        except IndexError:
            now_user = ''
        tmp = {'user': now_user, 'password': now_password}
        config.append(dict(data, **tmp))
    return config
    

def resolve_config(data):
    if not data:
        return None
    total_config = list()
    for info  in data:
        for k, v in info.items():
            #total_config.append(v)
            total_config.append({'{}'.format(k):format_config(v)})
    return total_config


def mysql_check(config):
    if config is None:
        # TODO config is Null igone check
        return None
    result_info = list()
    for info in config:
        for k,v in info.items():
            result_info.extend(check_test_mysql(v))
            #[{'user': 'starling_finworks_rw', 'host': '192.168.1.220', 'password': ['tBpncXu17CEZjJPjIy'], 'port': '4059', 'database': 'starling_finworks'}]
            #print k, v
    return result_info

def check_test_mysql(config):
    ERROR_INFO = ''
    info_list = list()
    table_is = 'No'
    for info_config in config:
        now_config = {
                'host': info_config['host'],
                'password': info_config['password'],
                'port': int(info_config['port']),
                'database': info_config['database'],
                'user': info_config['user'],
                'charset': 'utf8',
                'connection_timeout': 10
                }
        try:
            cnn=mysql.connector.connect(**now_config)
            cursor = cnn.cursor()
            cursor.execute('show tables')
            if cursor.fetchall():
                table_is = 'Yes'
            else:
                table_is = 'No'
            ERROR_IS = False
            ERROR_INFO = ''
            cursor.close()
            cnn.close()
        except mysql.connector.Error as e:
            ERROR_INFO = str(e)
            ERROR_IS = True
        if ERROR_IS:
            status = 'Failed'
        elif not ERROR_IS and table_is == 'Yes':
            status = 'Success'
        elif not ERROR_IS and table_is == 'No':
            status = 'Waring'
        else:
            status = 'info'

        info_list.append([
            now_config.get('host', ''),
            str(now_config.get('port', '')),
            now_config.get('user', ''),
            now_config.get('password', ''),
            now_config.get('database', ''),
            table_is,
            status,
            ERROR_INFO
            ])
    return info_list
        


if __name__ == '__main__':

    default_path = "/data/conf"
    parser = argparse.ArgumentParser(description="MySQL connect test",add_help=True)
    parser.add_argument("-p", metavar="project", help="project name")
    parser.add_argument("--path", metavar="Absolute path", help="config path /data/config/harbor/prod.properties")

    args = parser.parse_args()

    project = args.p
    abs_path = args.path
   
    if abs_path is not None:
        filename = args.path
    elif project is not None:
       filename = os.path.join(root, project, file_name)
    else:
       parser.print_help()
       sys.exit(1)
    if not os.path.exists(filename):
        print "{0} 文件不存在!".format(filename)
        sys.exit(1)

    data = read(filename)
    echo = Echo()
    config = get_config(data)
    if config:
        total_config = resolve_config(config)
        for info in mysql_check(total_config):
            echo.make_echo(info)
        echo.echo()