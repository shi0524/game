# -*- coding: utf-8 –*-

import time
import settings
from gconfig import game_config
from lib.db import ModelBase, ModelTools
from lib.core.environ import ModelManager


BAN_INFO_MESSAGE = {
    'expire'      : u'我们已对您的账号封停至 {} ！\n',
    'forever'     : u'我们已对您的账号进行永久封停！\n',
    'reason'      : u'由于您{}，',
    'no_reason'   : u'由于您在游戏中进行了违规操作，',
    'basic_start' : u'亲爱的玩家，您好：',
    'basic_end'   : u'如有疑问，请联系官方客服Q群：{}，感谢您的支持！',
}


class User(ModelBase):
    """ 玩家类
    """

    ADD_POINT_TIME = 60 * 6                 # 6分钟恢复一点体力
    MAX_ACTION_POINT = 120                  # 最大体力上限

    def __init__(self, uid):
        self.uid = uid

        self._attrs = {
            '_name': '',                    # 名字
            'level': 1,                     # 等级
            'exp': 0,                       # 经验
            'vip': 0,                       # vip 等级
            'vip_exp': 0,                   # vip 经验
            'blacklist': [],                # 黑名单
            'action_point': 0,              # 体力
            'action_point_updatetime': 0,   # 刷新时间
            'coin': 0,                      # 金币
            'diamond_free': 0,              # 免费钻石
            'diamond_charge': 0,            # 付费钻石
        }

        # 特殊信息(账号、平台等信息)
        self.specil_attrs = {
            'account': '',                  # 注册账户
            'tpid': '',                     # 平台id
            'register_ip': '',              # 注册IP
            'register_time': '',            # 注册时间
            'active_ip': 0,                 # 上一次请求IP
            'active_time': 0,               # 上一次请求时间
            'language_sort': '0',           # 使用语言
            'is_ban': 0,                    # 是否封号, 0: 表示不封, 1: 表示封禁
            'login_days': [],               # 登录日期
        }
        self._attrs.update(self.specil_attrs)

        self._cache = {}
        super(User, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server_name='', **kwargs):
        o = super(User, cls).get(uid, server_name=server_name, **kwargs)
        o.father_server_name = settings.get_father_server(o._server_name)
        o.config_type = game_config.get_config_type(o.father_server_name)
        return o

    @property
    def name(self):
        """The name property.
        """
        name = self._name
        return name

    def diamond_property():
        doc = "The diamond property."

        def fget(self):
            return self.diamond_free + self.diamond_charge

        def fset(self, value):
            # 1. 加钻石，都加到免费中
            # 2. 减钻石, 先消耗charge，再消耗free
            # 实现的效果：从diamond添加都加到free；消耗优先消耗charge，再消耗free；只能手动用diamond_charge添加付费金币
            diff_diamond = value - (self.diamond_free + self.diamond_charge)
            if diff_diamond < 0:    # 减钻石
                remain_diamond = self.diamond_charge + diff_diamond
                if remain_diamond < 0:
                    self.diamond_charge = 0
                    self.diamond_free = value
                else:
                    self.diamond_charge = remain_diamond

            elif diff_diamond > 0:  # 加钻石
                self.diamond_free += diff_diamond

        return locals()
    diamond = property(**diamond_property())

    def fresh(self):
        """ 刷新
        :return:
        """
        is_save = False

        now = int(time.time())
        today = time.strftime('%F')
        week = time.strftime('%W')      # (00-53) 星期一为星期的开始

        # 刷新体力
        div, mod = divmod(now - self.action_point_updatetime, self.ADD_POINT_TIME)
        if not self.is_point_max() and div > 0:
            self.add_action_point(div)
            self.action_point_updatetime = now - mod

    def update_active_time(self, req):
        """
        更新登录状态
        :return:
        """
        self.active_ip = req.headers.get('X-Real-Ip', '') or req.remote_ip
        ts = int(time.time())
        if not self.active_time:
            self.active_time = ts
        # if not self.online_time:
        #     self.online_time = ts
        today = time.strftime('%F')
        if today not in self.login_days:
            self.login_days.append(today)
        self.active_time = ts

    def is_point_max(self):
        """ 体力是否已满
        :return:
        """
        return self.action_point >= self.MAX_ACTION_POINT

    def add_action_point(self, point, fcoce=False, save=False):
        """ 加体力
        :param point: 体力值
        :param fcoce: 是否强制加体力
        :param save: 是否保存
        :return:
        """
        point = int(point)
        if not fcoce:
            if self.action_point < self.MAX_ACTION_POINT:
                self.action_point = min(self.MAX_ACTION_POINT, self.action_point + point)
        else:
            self.action_point += point

        if save:
            self.save()

    def decr_action_point(self, point, save=False):
        """ 扣除体力
        :param point:
        :param save:
        :return:
        """
        if self.action_point < point:
            return False

        # 体力从满减少到不满时, 更新更新时间
        if self.action_point - point <= self.MAX_ACTION_POINT:
            self.action_point_updatetime = int(time.time())

        self.action_point -= point

        if save:
            self.save()

ModelManager.register_model('user', User)
