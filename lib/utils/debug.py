# -*- coding: utf-8 –*-

import os
import sys
import logging
import socket
import time
import datetime
import hashlib
from functools import wraps
from mail import send_sys_mail
from collections import defaultdict

# 缓存服务器端报错信息
CLIENT_EXCEPTION_CACHES = defaultdict(int)
CLIENT_EXCEPTION_TIMES = 2


def print_log_maker(frame_num):
    def print_log_embryo(*args):
        """# print: 将s打印至log_stdout
        """
        f = sys._getframe(frame_num)
        rv = (os.path.normcase(f.f_code.co_filename), f.f_code.co_name, f.f_lineno)
        logging.critical('='*10+'  LOG '+str(datetime.datetime.now())+' %f START  '%time.time()+'='*11)
        logging.critical('='*8+'  AT %s: %s: %d: '%rv+'='*8)
        l = [str(i) for i in args]
        logging.critical('|| '+', '.join(l))
        logging.critical('='*35+'  LOG END  '+'='*35+'\n\n')
    return print_log_embryo

print_log = print_log_maker(1)


def get_stack_info(level=5):
    data = []
    for i in xrange(1, level):
        f = sys._getframe(i)
        rv = (os.path.normcase(f.f_code.co_filename), f.f_code.co_name, str(f.f_lineno))
        data.append(' '.join(rv))
    return '\n'.join(data)


def track_upon(n=5):
    """# track_upon: docstring
    args:
        n=3:    ---    arg
    returns:
        0    ---
    """
    for i in xrange(2, n):
        print_log_maker(i)(i)


def md5(s):
    """# md5: docstring
    args:
        s:    ---    arg
    returns:
        0    ---
    """
    return hashlib.md5(str(s)).hexdigest()


def trackback(msg='', exc_info=None):
    logging.critical(msg, exc_info=sys.exc_info())

try:
    LOCAL_IP_STR = os.popen('''ifconfig | grep 'inet ' | grep -v '127.0.0.1' ''').read()
except:
    LOCAL_IP_STR = ''


def error_mail(debug, addr_list):
    """ log exception decorator for a view,
    """
    def wrapper(func):

        @wraps(func)
        def _decorator(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except:
                import traceback, resource
                tb = traceback.format_exc()
                form = ''
                if len(self.request.arguments) > 0:
                    form_list = []
                    for k, v in self.request.arguments.iteritems():
                        form_list.append('%s="%s"' % (k, v))
                    form = '\n'+'\n'.join(form_list)
                log_dict = [
                    ('date', datetime.datetime.now()),
                    ('hostname', LOCAL_IP_STR if LOCAL_IP_STR else socket.gethostname()),
                    ('pid', int(os.getpid())),
                    ('rss', int(resource.getrusage(resource.RUSAGE_SELF)[2])),
                    ('', '\n\n'),
                    ('url', self.request.full_url()),
                    ('method', self.request.method),
                    ('remote', self.request.headers.get('X-Real-Ip', '')),
                    ('form',  form),
                    ('', '\n\n'),
                    ('class_method', "%s.%s" % (self.__class__.__module__, self.__class__.__name__)),
                    ('tb', tb),
                ]

                l = []
                for k, v in log_dict:
                    l.append('%s: "%s"' % (k, v))
                s = '\n'.join(l)
                import settings
                if debug:
                    subject = '[%s ERROR MAIL] - %s' % (settings.ENV_NAME, self.request.arguments.get('method', '[other method]'))
                    # subject = '[ERROR MAIL] '+settings.ENV_NAME+': '+socket.gethostname()+': '+tb.splitlines()[-1]
                    # 发邮件(相同的报错内容一天只发5次)
                    content_md5 = md5(tb)
                    had_num = CLIENT_EXCEPTION_CACHES[content_md5] + 1
                    if had_num <= CLIENT_EXCEPTION_TIMES:
                        rc = send_sys_mail(addr_list, subject, s)
                        CLIENT_EXCEPTION_CACHES[content_md5] += 1
                        print_log('error_mail %s rc: %s' % (s, str(rc)))
                else:
                    rc = 0
                    print_log('error_mail %s rc: %s' % (s, str(rc)))
                raise
            return result

        return _decorator

    return wrapper


def get_traceback_info(*args):
    import traceback, resource
    tb = traceback.format_exc()
    log_dict = [
        ('date', datetime.datetime.now()),
        ('hostname', '{} {}'.format(socket.gethostname(), LOCAL_IP_STR)),
        ('pid', int(os.getpid())),
        ('rss', int(resource.getrusage(resource.RUSAGE_SELF)[2])),
        ('', '\n\n'),
        ('tb', tb),
        ('', '\n\n'),
        ('args', ' '.join([str(i) for i in args])),

    ]
    l = []
    for k, v in log_dict:
        l.append('%s: "%s"' % (k, v))
    s = '\n'.join(l)
    return s
