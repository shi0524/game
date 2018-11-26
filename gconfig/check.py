# -*- coding: utf-8 –*-

import time


REWARD_CHECK_MAPPING = {
    # sort:{'num':限制数量, 'msg': 返回信息}
    1: {'num': 999999, 'msg': 'silver'},                # 银币大于999999
    2: {'num': 999999, 'msg': 'coin'},                  # 金币大于999999
    3: {'num': 2888, 'msg': 'diamond'},                 # 钻石大于2888
}

def check_reward_counts(x):
    message = None
    # 奖励存在检查
    for reward in x:
        if len(reward) == 3:
            sort, tid, num = reward
        else:
            sort, tid, num, lv = reward
        sort = int(sort)
        num = int(num)
        if sort in REWARD_CHECK_MAPPING.keys():
            if num > REWARD_CHECK_MAPPING[sort]['num']:
                return 'the %s(sort is %s) nums out of range!!!' % (REWARD_CHECK_MAPPING[sort]['msg'], sort)
            else:
                return message
        else:
            return message
    return message