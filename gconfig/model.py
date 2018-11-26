# -*- coding: utf-8 –*-

import time
import types
import settings
from lib.utils.singleton import Singleton
from models.config import Config, ConfigVersion, ConfigMd5
from gconfig.trans import trans_config
from gconfig.config_contents import mapping_config


class ReadonlyDict(dict):
    """ 防止操作过程中更改配置
    """

    def __readonly__(self, *args, **kwargs):
        raise RuntimeError('cantnot modify readonly dict')
    __setitem__ = __readonly__
    __delitem__ = __readonly__
    pop = __readonly__
    popitem = __readonly__
    clear = __readonly__
    setdefault = __readonly__
    del __readonly__


class ReadonlyList(list):
    """ 防止操作过程中更改配置
    """

    def __readonly__(self, *args, **kwargs):
        raise RuntimeError('cantnot modify readonly list')

    __setitem__ = __readonly__
    __delitem__ = __readonly__
    __iadd__ = __readonly__
    __imul__ = __readonly__
    pop = __readonly__
    append = __readonly__
    extend = __readonly__
    insert = __readonly__
    remove = __readonly__

    del __readonly__


def make_readonly(x, deep=0):
    if x.__class__ is list:
        d = []
        for i in x:
            d.append(make_readonly(i, deep+1))
        return ReadonlyList(d)
    elif x.__class__ is dict:
        d = {}
        for k, v in x.iteritems():
            d[k] = make_readonly(v, deep+1)
        return d if deep else ReadonlyDict(d)
    return x


class GameConfigMixIn(object):
    """配置嵌入类
    """
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.MUITL_LAN = {'0': 'TW', '1': 'CN'}

        ########## mapping ##########
        self.error_mapping = {}
        ########## mapping ##########

    def reset(self):
        """ 更新配置后重置数据
        """
        self.error_mapping.clear()

    def get_config_type(self, server_name, now=None):
        """ 获取配置类型
        :param server_name:
        :param now:
        :return:
        """
        server_type = self.server_type
        now = now or time.strftime(self.TIME_FORMAT)

        config = server_type.get('server_name')
        if config and now >= config['time']:
            config_type = config['type']
        else:
            config_type = settings.SERVERS.get(server_name, {}).get('config_type', 1)
        return int(config_type)

    def get_lan_error_msg(self, lan):
        msg = self.get_error_mapping().get(lan, {})
        return msg

    def get_error_mapping(self):
        """ 错误提示语
            MUITL_LAN = {'0': 'CN', '1': 'TW', '2': 'EN'}
        """
        if not self.error_mapping:
            self.error_mapping = {
                '0': {},
                '1': {},
                '2': {},
            }
            for v in self.error.itervalues():
                error_id = v['error_id']
                self.error_mapping['0'][error_id] = v['chinese']
                self.error_mapping['1'][error_id] = v['traditional_chinese']
                self.error_mapping['2'][error_id] = v['english']
        return self.error_mapping


class GameConfig(GameConfigMixIn):

    __metaclass__ = Singleton

    IGONE_NAME = ('keys', 'locked', 'ver_md5')

    def __init__(self):
        super(GameConfig, self).__init__()
        self.locked = True
        self.keys = []
        self.ver_md5 = ''
        self.versions = {}
        self.reload()
        self.locked = False

    def __getattribute__(self, name):
        """ 获取属性
        :param name: 属性名
        :return:
        """
        value = GameConfigMixIn.__getattribute__(self, name)

        if isinstance(value, types.MethodType):
            return value

        keys = GameConfigMixIn.__getattribute__(self, 'keys')
        if name not in keys and not GameConfigMixIn.__getattribute__(self, 'locked') and name not in GameConfigMixIn.__getattribute__(self, 'IGONE_NAME'):
            keys.append(name)
        return value

    def reload(self):
        """ 更新进程配置
        :return:
        """
        self.locked = True
        cm = ConfigMd5.get()
        if cm.ver_md5 == self.ver_md5:
            self.locked = False
            return False

        cv = ConfigVersion.get()
        if cv.versions and cv.versions == self.versions:
            self.locked = False
            return False

        cv_save = False
        for name, v in mapping_config.iteritems():

            # 配置 转换
            if name in []:
                pass

            cv_version = cv.versions.get(name)
            if cv_version and self.versions.get(name) == cv_version:
                continue

            c = Config.get(name)
            if cv_version and c.version != cv_version:
                if settings.CONFIG_SWITCH:
                    cv.versions[name] = c.version
                    cv_save = True

            if v[0]:    # 加载的策划配置的xlsx
                setattr(self, name, make_readonly(c.value))

                if cv_version:  # 设置服务器版本号
                    self.versions[name] = cv_version
            elif cv_version:
                setattr(self, name, make_readonly(c.value))

                # 设置服务器版本号
                self.versions[name] = cv_version

        if cv_save:
            cv.save()

        self.ver_md5 = cm.ver_md5

    def upload(self, file_name, xl=None):
        """ 上传一个文件
        :param file_name:
        :param xl:
        :return:
        """
        self.locked = True

        save_list = []
        warning_msg = []
        data = trans_config(file_name, xl)
        if not data:
            self.locked = False
            return save_list, []

        cv = ConfigVersion.get()
        for config_name, m, config in data:
            check_warning = config.pop('check_warning', [])
            if check_warning:
                warning_msg.extend(check_warning)
            if cv.versions.get(config_name) == m:
                continue
            c = Config.get(config_name)
            c.update_config(config, m, save=True)
            cv.update_version(config_name, m)
            save_list.append(config_name)

        if save_list:
            cv.save()
        self.locked = False
        return save_list, warning_msg

    def refresh(self):
        """刷新配置, 用于进程加载配置
        """
        if not settings.CONFIG_SWITCH:
            return False

        self.locked = True
        cv = ConfigVersion.get()
        cm = ConfigMd5.get()
        ver_md5 = cm.generate_md5(cv.versions)
        if ver_md5 == cm.ver_md5:
            self.locked = False
            return False

        cm.update_md5(cv.versions, gen_md5=ver_md5, save=True)
        self.locked = False
        return True
