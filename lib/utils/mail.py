# -*- coding: utf-8 –*-


import os
import json

#                 正文       title  addrs
SYS_MAIL_CMD = """echo '%s' | mail -s '%s' %s"""


def send_sys_mail(addr_list, subject, body):
    """# send_sys_mail: 用系统名义给人发邮件
    args:
        addr_list: 发件人的list
        subject: 邮件标题
        body: 邮件正文
    returns:
        0    ---
    """
    cmd = SYS_MAIL_CMD % (body, subject, ','.join(addr_list))
    os.system(cmd)


def send_dingtalk(addr_url, subject, body):
    """
    发送到 钉钉
    """
    if addr_url:
        info = json.dumps({'text': {'content': '%s\n\n%s' % (subject, body)}, 'msgtype': 'text'})
        command = "curl %s -H 'Content-Type: application/json' -d '%s' &" % (addr_url, info)
        os.system(command)