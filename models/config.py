# -*- coding: utf-8 –*-

import time
import settings
from lib.db import ModelBase, ModelTools
from lib.utils import md5
from lib.db import get_redis_client


class Config(ModelBase):
    """配置类
    """
    SERVER_NAME = 'master'
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'value': {},
            'version': '',
            'last_update_time': '',
        }
        super(Config, self).__init__(self.uid)

    def update_config(self, value, version, save=True):
        """更新配置
        """
        self.value = value
        self.version = version
        self.last_update_time = time.strftime(self.TIME_FORMAT)

        if save:
            self.save()


class ConfigMd5(ModelBase):
    """ver_md5: 所有配置版本号生成的MD5值
    """
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_md5'
        self._attrs = {
            'ver_md5': '',
        }
        super(ConfigMd5, self).__init__(self.uid)

    @classmethod
    def get(cls, *args, **kwargs):
        return super(ConfigMd5, cls).get('config_md5', cls.SERVER_NAME, *args, **kwargs)

    @classmethod
    def generate_md5(cls, versions):
        """根据配置版本号生成 md5 值
        """
        versions_sort = sorted(versions.iteritems(), key=lambda x: x[0])
        return md5(versions_sort)

    def update_md5(self, versions, gen_md5=None, save=False):
        """更新MD5值
        :param versions:
        :param gen_md5:
        :return:
        """
        self.ver_md5 = gen_md5 or self.generate_md5(versions)
        if save:
            self.save()

    def generate_custom_md5(self, data):
        """生成自定义MD5, 用于自定义数据, data中支持复杂类型 dict, set, list, tuple
        """
        if isinstance(data, (dict, set, list, tuple)):
            return md5(repr(data))
        return md5(data)


class ConfigVersion(ModelBase):
    """配置版本号
    """
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_version'
        self._attrs = {
            'versions': {}
        }
        super(ConfigVersion, self).__init__(self.uid)

    @classmethod
    def get(cls, *args, **kwargs):
        return super(ConfigVersion, cls).get('config_version', cls.SERVER_NAME, *args, **kwargs)

    def update_version(self, config_name, hex_version, save=False):
        """更新配置版本号
        """
        self.versions[config_name] = hex_version
        if save:
            self.save()


class ConfigRefresh(object):
    FLAG_KEY = 'config_refresh_key'
    TEXT_KEY = 'config_refresh_text_key'
    CLIENT = get_redis_client(settings.SERVERS['master']['redis'])

    @classmethod
    def set_updated(cls):
        cls.CLIENT.delete(cls.FLAG_KEY)

    @classmethod
    def refresh(cls, flag, msg):
        if flag:
            cls.CLIENT.set(cls.FLAG_KEY, 1)
        else:
            cls.CLIENT.delete(cls.FLAG_KEY)
        cls.CLIENT.set(cls.TEXT_KEY, msg)

    @classmethod
    def check(cls):
        from gconfig import game_config

        refresh_flag = cls.CLIENT.get(cls.FLAG_KEY)
        all_config_version = game_config.ver_md5
        refresh_msg = cls.CLIENT.get(cls.TEXT_KEY) or ''
        refresh_msg = refresh_msg.decode('utf-8')

        return refresh_flag or 0, all_config_version, refresh_msg
