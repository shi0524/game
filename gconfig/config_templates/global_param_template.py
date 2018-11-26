# -*- coding: utf-8 –*-

# 策划自定义变量配置
global_parameter_raw = {
    'uk':                   ('key',                     'str'),             # key
    'value':                ('value',                   'unicode'),         # 字段
    'type':                 ('type',                    'str'),             # 类型
}

# 后端报错提示语
error = {
    'uk':                   ('id',                      'int'),             # id
    'error_id':             ('error_id',                'str'),             # id
    'chinese':              ('chinese',                 'unicode'),         # 简体中文
    'traditional_chinese':  ('traditional_chinese',     'unicode'),         # 繁体中文
    'english':              ('english',                 'str'),             # 英文
}

# 版本强制更新表
version = {
    'uk': ('platform', 'str'),
    'version': ('version', 'str'),
    'url': ('url', 'str'),
    'msg': ('msg', 'unicode'),
}

