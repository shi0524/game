# -*- coding: utf-8 –*-

import datetime
import cPickle as pickle
from hashlib import md5
from lib.db import ModelTools


class Admin(ModelTools):
    """管理员
    """
    SERVER_NAME = 'master'
    ADMIN_PREFIX = 'game_admin'         # 用于存储hash表
    redis = ModelTools.get_redis_client(SERVER_NAME)

    def __init__(self, username=None):
        self.username = username                    # 管理员账号
        self.password = ''                          # 管理员密码
        self.email = ''                             # 管理员邮箱
        self.last_ip = '0.0.0.0'                    # 最后登录IP
        self.last_login = datetime.datetime.now()   # 最后登录时间
        self.permissions = {}                       # 管理员权限
        self.is_super = False                       # 是否是超管
        self.disable = False                        # 是否禁用该管理员

    @classmethod
    def get(cls, username):
        d = cls.redis.hget(cls.ADMIN_PREFIX, username)
        if d:
            o = cls()
            o.__dict__.update(pickle.loads(d))

    @classmethod
    def get_all_user(cls):
        """获取所有的管理者
        """
        d = cls.redis.hgetall(cls.ADMIN_PREFIX)
        return {k: eval(pickle.loads(v)) for k, v in d.iteritems()}

    def save(self):
        if self.password and not self.password[0] == '\x01':
            self.password = '\x01' + md5(self.password).hexdigest()
        d = self.__dict__
        self.redis.hset(self.ADMIN_PREFIX, self.username, pickle.dumps(repr(d)))

    def set_password(self, raw_password):
        """设置密码
        :param raw_password:
        :return:
        """
        self.password = raw_password

    def check_password(self, raw_password):
        """检查密码
        :return:
        """
        if self.password and self.password[0] == '\x01':
            return self.password == '\x01' + md5(raw_password).hexdigest()
        else:
            return self.password == raw_password

    def set_last_login(self, l_time, l_ip):
        """设置最后一次登录时间和IP地址
        """
        self.last_login = l_time
        self.last_ip = l_ip

    def delete(self):
        """删除管理员
        """
        self.redis.hdel(self, self.ADMIN_PREFIX, self.username)

    def check_permission(self, module_name, method_name):
        """检查权限
        :param module_name:
        :param method_name:
        :return:
        """
        if module_name == 'menu':
            return True
        if self.disable:
            return False
        if self.is_super:
            return True
        if method_name in self.permissions.get(method_name, []):
            return True
        return False