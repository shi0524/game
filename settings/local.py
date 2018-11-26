# -*- coding: utf-8 –*-


DEBUG = False                           # 是否是 debug 环境
PLATFORM = 'game_shi'                   # 平台标识
PRODUCT_NAME = '石头'                    # 平台名
MAIL_SENDING = False                    # 是否发报错邮件
DECRYPT_BATTLE_DATA = False             # 必须战斗加密
SESSION_SWITCH = False                  # session 开关
SESSION_EXPIRED = 86400                 # session 过期时间
APP_STORE_BID_LIST = []                 # ios appstore 绑定游戏id
ADMIN_LIST = [
    '1440255785@qq.com',                # 余风
]
DINGTALK = ''
URL_PARTITION = 'game'                  # 路径拼接符
SERVERS = {}                            # 区服信息

app_nginx = 'localhost'
redis_ip = 'localhost'

host_list = [
    # server    server_host     redis_ip     redis_port redis_db config_type
    ('s1',      app_nginx,      redis_ip,       7000,       0,      1),
    ('s2',      app_nginx,      redis_ip,       7000,       0,      1),
    ('s3',      app_nginx,      redis_ip,       7000,       0,      1),
    ('s4',      app_nginx,      redis_ip,       7000,       0,      1),
    ('s5',      app_nginx,      redis_ip,       7000,       0,      1),
]

# redis db 配置
cache_db = {
    'server': 0,        # 区服
    'master': 1,        # master
    'global': 2,        # 全局数据
}

# redis cache 配置
REDIS_CACHE = {
    'host': 'localhost',
    'port': 7000,
    'socket_timeout': 3,
    'db': 0,
    # 'passwd': '',
}

GLOBAL_CACHE = dict(REDIS_CACHE, db=cache_db['global'])     # 全局数据
MASTER_CACHE = dict(REDIS_CACHE, db=cache_db['master'])     # master cache

# mysql_setting MYSQL 相关配置
PAYLOG_HOST = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'root123',
    'db': 'game_shi',
    'table_prefix': 'paylog',
    'connect_timeout': 5,
}

# 消费信息存储
SPEND_HOST = dict(PAYLOG_HOST, table_prefix='spendlog')


# 区服信息
SERVERS['master'] = {'redis': MASTER_CACHE}
for i in host_list:
    hosts = i[1].split(';')
    SERVERS[i[0]] = {
        'server': ['http://%s/' % x for x in hosts],
        'config_type': i[5],
        'father_server': i[6] if len(i) > 6 and i[6] else i[0],
        'redis': {'host': i[2], 'port': i[3], 'socket_timeout': 5, 'db': i[4]}
    }
