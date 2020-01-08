#! /srv/python2/bin/python
#! -*- coding:utf8 -*-
import os
import sys
import redis
import re
import argparse
from prettytable import PrettyTable
import random


class Echo:
    def __init__(self):
        self.obj = PrettyTable(['host', 'port',  'password', 'status', 'error info'])
    
    def make_echo(self, data):
        self.obj.add_row(self.__format(data))

    def echo(self):
        print self.obj

    def __format(self, data):
        if data[-2] != 0:
             data[-2] = '\033[1;31mFailed\033[0m'
             data[-1]  = '\033[1;31m{}\033[0m'.format(data[-1])
        else:
            data[-2] = '\033[1;32mSuccess\033[0m'
            data[-1] = '\033[1;32m{}\033[0m'.format(data[-1])

        return data


def filter(file):
     host = ""
     port = ""
     password = ""
     cache_host = ""
     cache_password = ""
     cache_port = ""
     with open(file) as f:
         for line in f:
             if re.match(r"^$|^#", line.strip()):
                 continue
             host_match = re.match(r"redis.host=(.*)", line.strip())
             if host_match:
                 host = host_match.group(1)
                 continue
             port_match = re.match(r"redis.port=(.*)", line.strip())
             if port_match:
                port = int(port_match.group(1))
                continue
             password_match = re.match(r"redis.password=(.*)", line.strip())
             if password_match:
                password = password_match.group(1)
                continue
             cache_host_match = re.match(r"cache.redis.host=(.*)", line.strip())
             if cache_host_match:
                 cache_host = cache_host_match.group(1)
                 continue
             cache_port_match = re.match(r"cache.redis.port=(.*)", line.strip())
             if cache_port_match:
                cache_port = int(cache_port_match.group(1))
                continue

             cache_password_match = re.match(r"cache.redis.password=(.*)", line.strip())
             if cache_password_match:
                 cache_password = cache_password_match.group(1)
                 continue

             


     return [{"host": host, "password": password, "port": port}, {"host": cache_host, "password": cache_password, "port": cache_port}]



def check_redis(data):
    result_data = list()
    for config in data: 
        if not len(config.get("host", "").strip()) or not config.get("port", 0) or not len(config.get("password", "").strip()):
            continue
        test_data = "op_redis_check_{0}".format(int(random.random()*10000))
        redis_result = redis.Redis(host=config.get('host','127.0.0.1'), port=int(config.get('port', 20)), password=config.get('password', 'xx'))
        tmp_data = [config.get('host','127.0.0.1'), config.get('port', 20), config.get('password', 'xx')]
        try:
           if redis_result.ping():
               if not redis_result.set('op_redis_check','success', 10):
                   tmp_data.append(1)
                   tmp_data.append("redis set key fail!")
               if not redis_result.get('op_redis_check'):
                   tmp_data.append(1)
                   tmp_data.append("redis get key fail!")
               tmp_data.append(0)
               tmp_data.append("redis check success")
           else:
               tmp_data.append(0)
               tmp_data.append("redis ping fail!")
        except redis.exceptions.ResponseError as e:
               tmp_data.append(0)
               tmp_data.append("redis auth fail!")
        except redis.exceptions.ConnectionError as e:
               tmp_data.append(0)
               tmp_data.append("redis connection fail!")
        result_data.append(tmp_data)
    return result_data



if __name__ == '__main__':
    default_path = "/data/config"
    parser = argparse.ArgumentParser(description="Check redis server connect", epilog="check redis server")
    parser.add_argument("--path", metavar="path", help="project config path")
    parser.add_argument("-p", metavar="project name", help="project name")
    args = parser.parse_args()
    path = args.path
    project = args.p
    if path:
       current_path = path
    elif project:
       current_path = os.path.join(default_path, project, "prod.properties")
    else:
        parser.print_help()
        sys.exit(1)
    
    if not os.path.exists(current_path):
       print("{0} config file is not exists".format(current_path))
       sys.exit(1)
    redis_config = filter(current_path)
    result_data = check_redis(redis_config)
    echo = Echo()
    if not result_data:
        sys.exit(1)
    for printf_data in result_data:
       echo.make_echo(printf_data)
    echo.echo()