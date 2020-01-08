#! /srv/python2/bin/python
#! -*- coding:utf8 -*-
import os
import sys
import re
import argparse
from prettytable import PrettyTable
from kazoo.client import KazooClient
from kazoo.handlers.threading import KazooTimeoutError
from kazoo.exceptions import NoNodeError
import logging



class Echo:
    def __init__(self):
        self.obj = PrettyTable(['host', 'port', 'status', 'error info'])
    
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
     cache_host = ""
     with open(file) as f:
         for line in f:
             if re.match(r"^$|^#", line.strip()):
                 continue
             host_match = re.match(r"dubbo.registry.address=zookeeper://([0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}:[0-9]{0,5})\S+", line.strip())
             if host_match:
                 host = host_match.group(1)
                 continue
             cache_host_match = re.match(r"dubbo.registry.address.userCenter=zookeeper://([0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}.[0-9]{0,3}:[0-9]{0,5})\S+", line.strip())
             if cache_host_match:
                 cache_host = cache_host_match.group(1)
                 continue

     return host.split(":"), cache_host.split(":")



def check_zookeeper(config):
    status_list = []
    for host in config:
        if not len(host[0].strip()):
            continue
        zk = KazooClient(hosts=":".join(host), timeout=5)
        try:
           zk.start()
           host.append(0)
           host.append("check success")
           status_list.append(host)
           '''
           if zk.exists("/op_zookeeper_check", watch=None):
               zk.create("/op_zookeeper_check", b"op zookeeper check")
           try:
               zk_get_result = zk.get("/op_zookeeper_check", watch=None)
               if zk_get_result:
                   zk.delete("/op_zookeeper_check", recursive=True)
           except NoNodeError:
               zk.stop()
               return False
           zk.stop()

            zk.stop()
          '''
        except KazooTimeoutError:
           host.append(1)
           host.append("zookeper connect timeout")
           status_list.append(host)
           zk.stop()
    return status_list



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="/var/log/zookepper.log")
    default_path = "/data/config"
    parser = argparse.ArgumentParser(description="Check zookeeper server connect", epilog="check zookeeper server")
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
    zookeeper_config = filter(current_path)
    result_zookeeper = check_zookeeper(zookeeper_config)
    if not result_zookeeper:
        sys.exit(1)

    echo = Echo()
    for printf_data in result_zookeeper:
       echo.make_echo(printf_data)
    echo.echo()