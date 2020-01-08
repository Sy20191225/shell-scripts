#! /srv/python2/bin/python
#! -*- coding:utf8 -*-

import os
import sys
import pika
from pika.exceptions import ProbableAuthenticationError
from pika.exceptions import ConnectionClosed
from pika.exceptions import ProbableAccessDeniedError
import re
import argparse
from prettytable import PrettyTable


class Echo:
    def __init__(self):
        self.obj = PrettyTable(['host', 'port', 'user', 'password', 'vhost', 'check_vhost', 'status', 'error info'])
    
    def make_echo(self, data):
        info_list = []
        for key in ["host", "port", "username", "password", "vhost", "check_vhost", "status", "msg"]:
            info_list.append(data.get(key, ''))
        self.obj.add_row(self.__format(info_list))

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

class Check:
    def __init__(self, host, username, password, port=5672, vhost="/op_check"):
        self.host = host
        self.vhost = vhost
        self.port = port
        self.username = username
        self.password = password
        self.message = ""
        self.check_status = False
        self.body = "op check"
        self.is_login = False
        try:
            rabbit_user_obj = pika.PlainCredentials(self.username, self.password)
            """add debug """
            print("debuge")
            print("username,password: ",self.username,self.password)
            rabbit_connent = pika.ConnectionParameters(self.host,self.port, self.vhost, rabbit_user_obj)
            print("host,port,vhost,obj: ",self.host,self.port, self.vhost, rabbit_user_obj)

            self.connection = pika.BlockingConnection(rabbit_connent)
            print("rabbit_connent: ",rabbit_connent)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='op_check')
            self.is_login = True
        except ProbableAuthenticationError:
            self.check_status = False
            self.message = "{0}:{1} rabbitmq auth fail!".format(self.host, self.port)
        except ConnectionClosed:
            self.check_status = False
            self.message = "{0}:{1} rabbitmq connection fail!".format(self.host, self.port)
        except ProbableAccessDeniedError:
            self.check_status = False
            self.message = "{0}:{1} rabbitmq check vhost not is exstis!".format(self.host, self.port)
        except Exception as e:
            self.check_status = False
            self.message = "{0}:{1} rabbitmq login in error: {2}".format(self.host, self.port, str(e))
  
            
        

    def send(self):
        if self.is_login:
            self.channel.basic_publish(exchange='', routing_key='op_check', body=self.body) 
            return True
        else:
            return False
        
    def receice(self):
       if self.is_login: 
           method_frame, header_frame, body = self.channel.basic_get('op_check')
           if method_frame:
              self.channel.basic_ack(method_frame.delivery_tag)
              if body.strip() == self.body:
                 self.check_status = True
                 self.message = "check success"
                 return True
              else:
                 self.check_status = False
                 self.message = "{0}:{1} queue message check fail".format(self.host, self.port)
                 return False
           else:
                 self.check_status = False
                 self.message = "{0}:{1} queue  message not exists".format(self.host, self.port)
       else:
           return False

    def check(self):
            if self.check_status:
                return {"status": 0, "msg": self.message}
            else:
                return {"status": 1, "msg": self.message}
                
    def close(self):
        self.connection.close()


def filter(file):
     host = ""
     user = ""
     vhost = ""
     port = 0
     password = ""
     with open(file) as f:
         for line in f:
             if re.match(r"^$|^#", line.strip()):
                 continue
             host_match = re.match(r"rabbit.host=(.*)", line.strip())
             if host_match:
                 host = host_match.group(1)
                 continue
             user_match = re.match(r"rabbit.username=(.*)", line.strip())
             if user_match:
                 user = user_match.group(1)
                 continue
             vhost_match = re.match(r"rabbit.vhost=(.*)", line.strip())
             if vhost_match:
                vhost = vhost_match.group(1)
                continue

             port_match = re.match(r"rabbit.port=(.*)", line.strip())
             if port_match:
                port = port_match.group(1)
                continue
             password_match = re.match(r"rabbit.password=(.*)", line.strip())
             if password_match:
                password = password_match.group(1)
                continue

     return {"host": host, "username": user, "vhost": vhost, "password": password, "port": int(port)}


if __name__ == '__main__':
    default_path = "/data/config"
    parser = argparse.ArgumentParser(description="Check rabbitmq server connect", epilog="need rabbitmq server create '/op_check' vhost")
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
    rabbit_mq = {
            "host": "192.168.93.53",
            "username": "op_check",
            "password": "rabbitmqtest",
            "port": 5672,
            "enable": False
            }
    if not rabbit_mq["enable"]:
        rabbit_mq = filter(current_path)

    #{'username': 'jek_finworks', 'vhost': '/jek_finworks', 'host': '192.168.57.156', 'password': 'cCW11MwCZOrWsh', 'port': 5672}
    if not len(rabbit_mq["username"].strip()) or not len(rabbit_mq["host"].strip()) or not len(rabbit_mq["password"].strip()) or not rabbit_mq["port"]:
       sys.exit(1)
    echo = Echo()
    rabbit_check = Check(rabbit_mq["host"], rabbit_mq["username"], rabbit_mq["password"], rabbit_mq["port"])
    if rabbit_check.send():
        rabbit_check.receice()
    
    result_data = rabbit_check.check()
    rabbit_mq["check_vhost"] = "/op_check"
    echo.make_echo(dict(rabbit_mq, **result_data))
    echo.echo()