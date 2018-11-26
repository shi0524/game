# -*- coding: utf-8 –*-

import re

# 命名规则  xxx_mapping


# mapping_config = {
#     # key: config_name, value: 表名,  是否前端可见
# }


def register_mapping_config(source, target):
    """ 注册提示消息
    :param source:
    :param target:
    :return:
    """
    for k, v in target.iteritems():
        if k in source:
            raise RuntimeError('config [%s] Already exists in %s' % (k, __file__))
        source[k] = v
    target.clear()


def register_handler():
    match = re.compile('^[a-zA-Z0-9_]+_mapping$').match
    g = globals()
    mapping = g['mapping_config']
    for name, value in g.iteritems():
        if match(name):
            register_mapping_config(mapping, value)


mapping_config = {
    # key: config_name, value: 表名,  是否前端可见
}


######################### 配置区域 #########################

global_param_mapping = {
    # key: config_name,         value: 表名,              是否前端可见
    'global_parameter_raw':     ('global_parameter_raw',    True),
    'error':                    ('error',                   False),
    'version':                  ('version',                 False),
}

server_template_mapping = {
    # key: config_name,         value: 表名,              是否前端可见
    'server_type':              ('server_type',             False),
}
######################### 配置区域 #########################

# 注册需要卸载最下面
register_handler()

