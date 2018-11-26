# -*- coding: utf-8 –*-


import time
import json
import settings
from lib.utils.debug import print_log
from models.config import ConfigRefresh


def to_json(obj):
    """# to_json: 将一些特殊类型转换为json
    args:
        obj:    ---    arg
    returns:
        0    ---
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(repr(obj) + ' is not json seralizable')


def user_status(mm):
    """ 用户状态

    :param mm:
    :return:
    """
    if mm is None:
        return {}

    user = mm.user

    data = {
        'uid': user.uid,
        'reg_time': user.register_time,     # 注册时间
        'name': user.name,
        'level': user.level,
        'exp': user.exp,
        'coin': user.coin,
        'vip': user.vip,
        'vip_exp': user.vip_exp,
        'diamond': user.diamond,
        'action_point': user.action_point,
        'action_point_updatetime': user.action_point_updatetime,
    }
    return data


def result_generator(rc, data, msg, mm):
    """ 统一生成返回格式

    :param rc: 接口状态
    :param data: 接口数据
    :param msg: 接口报错后的提示信息
    :param mm: ModelManager 对象管理类
    :return:
    """
    r = {
        'data': data,
        'status': rc,
        'msg': msg,
        'server_time': int(time.time()),
        'user_status': user_status(mm),
    }
    _, all_config_version, _ = ConfigRefresh.check()
    r['all_config_version'] = all_config_version
    if 'client_upgrade' in data:
        r['client_upgrade'] = data['client_upgrade']
    indent = 1 if settings.DEBUG else None
    r = json.dumps(r, ensure_ascii=False, separators=(',', ':'), encoding="utf-8", indent=indent, default=to_json)
    return r