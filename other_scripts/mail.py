#!/usr/bin/python
# -*- coding: UTF-8 -*-

import yagmail
import sys

from_user='xxxxxx@co-gro.com'
from_pwd='Q1w2e3'
from_host='smtp.exmail.qq.com'
from_portt='465'

#接收人列表
to_user = 'aaaa@co-gro.com'

#邮件标题
title = u'MySQL慢查询统计信息'

#邮件正文（接收参数1）
contents = sys.argv[1]

#附件（接收参数2）
DATE = sys.argv[2]

sql_select = '/root/mysql_slowLog_file/select/sql_select_' + DATE + '.txt'
report_name = '/root/mysql_slowLog_file/html/mysql_slow_' + DATE + '.html'
file = [sql_select, report_name]

#抄送人列表
c_user = 'bbbbb@co-gro.com'

#链接邮箱服务器
yag = yagmail.SMTP(user=from_user, password=from_pwd, host=from_host, port=from_portt)

# 发送邮件
yag.send(to_user, title, contents, file, c_user)

