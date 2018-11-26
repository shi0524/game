# -*- coding: utf-8 –*-

import os
import time
import json
import copy
import settings
from functools import wraps


def get_stat(mm):
    """ 玩家身上数据的统计
    :param mm:
    """
    return {
        'exp': mm.user.exp,                         # 经验
        'vip': mm.user.vip,                         # vip
        'vip_exp': mm.user.vip_exp,                 # vip经验
        'level': mm.user.level,                     # 等级
        'coin': mm.user.coin,                       # 金币
        'diamond': mm.user.diamond,                 # 钻石
        'diamond_free': mm.user.diamond_free,       # 免费钻石
        'diamond_charge': mm.user.diamond_charge,   # 付费钻石
    }


def stat(func):
    """

    :param func:
    :return:
    """
    @wraps(func)
    def decorator(self, *args, **kwargs):

        ###########################################################
        has_hm = getattr(self, 'hm', None)

        if has_hm:
            arguments = copy.deepcopy(self.hm.req.summary_params())
            mm = self.hm.mm
        else:
            arguments = copy.deepcopy(self.summary_params())
            mm = None

        method = arguments.get('method')
        method = method[0] if method else ''
        device_mark = arguments.pop('device_mark', [''])[0]
        platform = arguments.pop('pt', [''])[0]

        ignore_arg_name = ['method', 'user_token', 'mk']

        for arg_name in ignore_arg_name:
            if arg_name in arguments:
                del arguments[arg_name]

        user_stat_before = get_stat(mm)

        ###########################################################

        rc, data, msg, mm = func(self, *args, **kwargs)

        ###########################################################

        body = {
            'a_rst': [],
            'a_tar': arguments,
            'return_code': '0',
            'a_typ': method,
            'a_usr': '%s@%s' % (mm.user._server_name, mm.uid),
        }

        modify_args = data.pop('modify_args', None)
        if modify_args:
            delete_args = modify_args.get('delete')
            update_args = modify_args.get('update')
            if delete_args:
                for arg_name in delete_args:
                    if arg_name in arguments:
                        del arguments[arg_name]
            if update_args:
                arguments.update(update_args)

        # 非0返回将 return_code 记录用来分析常见错误返回
        if rc != 0:
            body['return_code'] = str(rc)
            return rc, data, msg, mm

        # 0 返回分析资源变化
        else:
            user_stat_after = get_stat(mm)
            resource_diff = []      # 资源变化列表
            ldt = time.strftime('%F %T')
            for k, v in user_stat_after.iteritems():
                _v = user_stat_before[k]
                if v != _v:
                    diff = v - _v
                    info = {
                        'obj': k,
                        'before': str(_v),
                        'after': str(v),
                        'diff': str(diff)
                    }
                    resource_diff.append(info)

            client_cache_udpate = data.get('_client_cache_update', {})
            old_data = data.pop('old_data', {})
            for class_type, class_type_value in client_cache_udpate.iteritems():
                old_data_key = mm.get_model_key(mm.uid, class_type)
                _old_data = old_data.get(old_data_key, {})

        body['a_rst'] = resource_diff
        dmp_data = {
            'body': body,
            'log_t': time.strftime('%F %T'),
            'device_mac': device_mark,
            'platform': platform,
            'account': mm.user.account,
            'level': str(mm.user.level),
            'exp': str(mm.user.exp),
            'vip_exp': str(mm.user.vip_exp),
            'coin': str(mm.user.coin),
            'diamond': str(mm.user.diamond),
        }

        # TODO
        """
        f_name = '%s_%s_%s' % (settings.ENV_NAME, os.getpid(), time.strftime('%Y%m%d'))
        log = get_log('action/%s' % f_name, logging_class=StatLoggingUtil, propagate=0)
        log.info(json.dumps(dmp_data, separators=(',', ':')))
        """

        ###########################################################

        return rc, data, msg, mm
    return decorator
