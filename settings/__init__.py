# -*- coding: utf-8 –*-




import os
import re
import time


DEBUG = True                            # 是否是 debug 环境
PLATFORM = ''                           # 平台标识
PRODUCT_NAME = '名字'                    # 平台名
SERVERS = {}                            # 所有区服
MAIL_SENDING = False                    # 是否发报错邮件
DECRYPT_BATTLE_DATA = False             # 必须战斗加密
SESSION_SWITCH = False                  # session 开关
SESSION_EXPIRED = 86400                 # session 过期时间
APP_STORE_BID_LIST = []                 # ios appstore 绑定游戏id
ADMIN_LIST = []                         # 报错邮件名单
CONFIG_NAME_LIST = []                   # 配置名列表
BROWSER = ''                            # 浏览器验证码
FRONTWINDOW = ''                        # 多点登录验证码

DEFAULT_BACKEND_ADMIN = [               # 初始化后台管理员
    ('test_admin', '123'),
]
DEFAULT_BACKEND_SUPER_ADMIN = [         # 后天超级管理员, 可实时获得后台添加的新功能权限
    ('super_admin', '123'),
]
CONFIG_SWITCH = False                   # 配置开关
DINGTALK = ''                           # 钉钉群消息robot
MIN_COMPRESS = 50                       # 数据最小压缩大小
ZIP_COMPRESS_SWITCH = True              # 数据压缩开关
CONFIG_UPDATE_TIME = 5                  # 配置更新的延迟时间 (单位：秒) 每隔几秒检测一次
ALL_DB_SERVERS = {}                     # 所有的服
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_ROOT = os.path.dirname(CUR_DIR) + os.path.sep


def import_check():
    """检查所有py文件
    """
    count = {}
    exclude_files = ('__init__',)
    exclude_dirs = ('scrips', 'upload_xls', 'logs')
    for path, dirs, files in os.walk(BASE_ROOT):
        if '/.' in path:
            continue
        package = path.replace(BASE_ROOT, '').replace('/', '.').replace('\\', '.')
        if not package:
            continue

        dir_name = package.split('.')[0]
        if dir_name in exclude_dirs:
            continue

        for name in files:
            if name[0] == '.':
                continue
            file_name, file_ext = os.path.splitext(name)
            if file_ext != '.py' or file_name in exclude_files:
                continue
            module = '.'.join((package, file_name))
            m = __import__(module, globals(), locals(), fromlist=[file_name])
            count[dir_name] = count.get(dir_name, 0) + 1

    print '------------------------- check fiels: %s -------------------------' % sum(count.values())
    for module, num in sorted(count.iteritems()):
        print '\t'.join(map(str, (module, num)))
    print '------------------------- check fiels: end -------------------------'


def set_env(env_name, server=None, *args, **kwargs):
    """
    :param env_name: 环境名
    :param server 服务类型 config: 配置服务器 app: 逻辑服务器 all: 所有权限
    """
    start_time = time.time()
    execfile(os.path.join(CUR_DIR, '%s.py' % env_name), globals(), globals())

    globals()['ENV_NAME'] = env_name
    if server:
        globals()['SERVER_SORT'] = server
        if globals()['SERVER_SORT'] in ('all', 'config',):
            globals()['CONFIG_SWITCH'] = True

    prefix = ''
    length = 1

    for k in globals()['SERVERS']:
        if k in ('master'):
            continue
        if prefix:
            temp = len(k[len(prefix):])
            if length < temp:
                length = temp
        else:
            for idx, i in enumerate(k):
                if not k[idx:].isdigit():
                    prefix += i
                else:
                    temp = len(k[idx:])
                    if length < temp:
                        length = temp

    pattern = re.compile('^%s\d{%s,%s}$' % (prefix, 1 + 7, length + 7)).match
    globals()['UID_PATTERN'] = pattern
    globals()['CN_NAME_PATTERN'] = re.compile(u"([\u4e00-\u9fa5]+)").match

    import_check()
    end_time = time.time()

    print end_time - start_time


def check_uid(uid):
    """ 检查uid格式是否正确
    :param uid:
    :return:
    """
    if not globals()['UID_PATTERN'](uid):
        return False
    return True


def get_father_server(server_name):
    """ 获取主服
    :param server_name:
    :return:
    """
    sc = globals()['SERVERS'][server_name]
    return sc.get('father_server', server_name)


def is_father_server(server_name):
    """ 判断是否是主服
    :param server_name:
    :return:
    """
    return server_name == get_father_server(server_name)


def set_debug_print():
    import sys
    import logging

    h = logging.getLogger('debug_print')
    h.write = h.critical
    old_stdout = sys.stdout
    sys.stdout = h