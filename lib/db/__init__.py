# -*- coding: utf-8 –*-


import redis
import settings
from lib.utils.zip_data import data_encode_by_pickle as data_encode
from lib.utils.zip_data import data_decode_by_pickle as data_decode


REDIS_CLIENT_DICT = {}      # 每一个redis都有一个pool


def make_redis_client(redis_config):
    """
    :param redis_config:    redis 配置
    :return:
    """
    try:
        if cmp(redis.VERSION, (2, 10, 1)) >= 0:
            pool = redis.BlockingConnectionPool(retry_on_timeout=True, **redis_config)
        else:
            pool = redis.BlockingConnectionPool(**redis_config)
    except:
        pool = redis.BlockingConnectionPool(**redis_config)

    redis_client = redis.Redis(connection_pool=pool)

    return redis_client


def get_redis_client(redis_config):
    """ 获取一个redis链接实例
    :param redis_config: {
                    'host': 'localhost',
                    'port': 7000,
                    'socket_timeout': 3,
                    'db': 0,
                    'passwd': '',
                }
    """
    client_key = '_'.join([redis_config['host'], str(redis_config['port']), str(redis_config['db'])])

    if client_key not in REDIS_CLIENT_DICT:
        client = make_redis_client(redis_config)
        REDIS_CLIENT_DICT[client_key] = client

    return REDIS_CLIENT_DICT[client_key]


def dict_diff(old, new):
    """判断一个字典数据变换前后差异
    :param old: 原始字典数据
    :param new: 最新字典数据
    :return: (数据更新, 移除key)
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    remove_keys = old_keys - new_keys       # 操作后被删除的key
    add_keys = new_keys - old_keys          # 操作后新添加的key
    same_keys = new_keys & old_keys         # 操作前后具有相同的key, 对比是否修改

    update = {}

    for k in same_keys:
        new_data = new[k]
        if old[k] != new_data:
            update[k] = new_data
    for k in add_keys:
        update[k] = new[k]
    return update, remove_keys


class ModelTools(object):
    """ModelTools 工具类
    """

    @classmethod
    def get_server_name(cls, uid):
        """根据 uid 获取服标识
        """
        x = uid[-7:]
        if not x.isdigit():
            return uid[:-5]
        return uid[:-7]

    @classmethod
    def get_redis_client(cls, server_name):
        """ 根据服标识获取redis实例
        :param server_name:
        """
        redis_config = settings.SERVERS[server_name]['redis']
        client_key = '_'.join([redis_config['host'], str(redis_config['port']), str(redis_config['db'])])
        client = REDIS_CLIENT_DICT.get(client_key)
        if not client:
            client = make_redis_client(redis_config)
            REDIS_CLIENT_DICT[client_key] = client
        return client

    @classmethod
    def _key_prefix(cls, server_name=''):
        if not server_name:
            server_name = cls.SERVER_NAME
        return "%s||%s||%s" % (cls.__module__, cls.__name__, server_name)

    @classmethod
    def _key_to_uid(cls, _key, server_name=''):
        """ 通过 _key 获取 uid
        """
        return _key.replace(cls._key_prefix(server_name) + '||', '')

    @classmethod
    def make_key_cls(cls, uid, server_name):
        """生成类相关的key
        """
        return cls._key_prefix(server_name) + "||%s" % str(uid)

    @classmethod
    def make_key(cls, uid='', server_name=''):
        """生成key
        """
        server_name = server_name or cls.SERVER_NAME
        return cls.__class__.make_key_cls(uid, server_name)

    @classmethod
    def run_data_version_update(cls, _key, o):
        """数据升级函数
        """
        next_dv = o._data_version__ + 1
        data_update_func = getattr(o, 'data_update_func_%d' % next_dv, None)
        while data_update_func and callable(data_update_func):
            o._data_version__ = next_dv
            data_update_func()
            if settings.DEBUG:
                print '%s.%s complate' % (_key, data_update_func.__name__)
            next_dv += 1
            data_update_func = getattr(o, 'data_update_func_%d' % next_dv, None)


class ModelBase(ModelTools):
    """基础数据类
    """
    SERVER_NAME = None
    _need_diff = ()         # 开关, 判断是否需要进行数据对比,如果需要, 则元组中的元素为需要的diff的key的名字

    def __new__(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        cls._attrs_base = {
            '_data_version__': 0,
        }
        cls._attrs = {}
        return object.__new__(cls)

    def __init__(self, uid=None):
        """
        :param uid:
        :return:
        """
        if not self._attrs:
            raise ValueError, '_attrs must be not empty'
        self._attrs_base.update(self._attrs)
        self.__dict__.update(self._attrs_base)
        self.uid = str(uid)
        self._model_key = None
        self._server_name = None
        self.redis = None
        self.mm = None
        self.model_status = -1      # -1 无状态 1 更改
        self.async_save = False
        self._old_data = {}
        self._diff = {}
        super(ModelBase, self).__init__()

    def _client_cache_update(self):
        """前端cache更新机制中数处理方法, 有些数据是需要特殊处理的
        """
        return self._diff

    @classmethod
    def loads(cls, uid, data, o=None):
        """数据反序列化
        """
        o = o or cls(uid)

        loads_data = data_decode(data)
        old_loads_data = data_decode(data)

        for k in cls._attrs_base:
            v = loads_data.get(k)
            if v is None:
                v = o._attrs_base[k]
                if k in cls._attrs_base[k]:
                    if k in cls._need_diff:
                        o._old_data[k] = v
            else:
                if k in cls._need_diff:
                    o._old_data[k] = old_loads_data[k]
            setattr(o, k, v)
        return o

    def dumps(self, compress=True):
        """数据序列化
        """
        r = {}

        for k in self._attrs_base:
            data = getattr(self, k)
            r[k] = data

            if k in self._need_diff:
                if k in self._old_data:
                    old_v = self._old_data[k]
                    if data != old_v:
                        if isinstance(data, dict):          # 判断是否是字典
                            update_data, remove_keys = dict_diff(old_v, data)
                        elif isinstance(data, list):        # 判断是否是列表
                            update_data, remove_keys = data, {}
                        else:
                            update_data, remove_keys = data, {}
                    else:
                        if isinstance(data, dict):
                            update_data, remove_keys = dict_diff(data, {})
                        elif isinstance(data, list):
                            update_data, remove_keys = data, {}
                        else:
                            update_data, remove_keys = data, {}

                    self._diff[k] = {
                            'update': update_data,
                            'remove': remove_keys,
                        }
        if compress:
            r = data_encode(r)
        return r

    def _save(self, uid='', server_name=''):
        """保存
        """
        if server_name:
            if server_name not in settings.SERVERS:
                raise KeyError('ERROR SERVER NAME: %s' % server_name)

        _key = self._model_key
        if not _key:
            if not server_name or self._server_name:
                server_name = self.SERVER_NAME
            if server_name not in settings.SERVERS:
                raise KeyError('ERROR SERVER NAME: %s' % server_name)
            self._server_name = server_name
            _key = self.make_key(uid, server_name)

        s = self.dumps()
        self.redis.set(_key, s)

        if settings.DEBUG:
            print 'model save: ', _key

    def save(self, uid='', server_name=''):
        """保存
        """
        if self.async_save:
            self.model_status = 1
        else:
            self._save(uid=uid, server_name=server_name)

    @classmethod
    def get(cls, uid, server_name='', mm=None, *args, **kwargs):
        """获取数据
        :param uid: uid
        :param server_name: 用于指定数据库列表
        :param mm: model 管理类
        :return:
        """
        if not server_name:
            server_name = cls.SERVER_NAME
        if not server_name:
            server_name = cls.get_server_name(uid)
        if server_name not in settings.SERVERS:
            raise KeyError('ERROR SERVER NAME: %s' % server_name)

        _key = cls.make_key_cls(uid, server_name)
        redis_client = cls.get_redis_client(server_name)

        o = cls(uid)
        o._server_name = server_name
        o._model_key = _key
        o.redis = redis_client
        o.pre_init()

        redis_data = redis_client.get(_key)

        if not redis_data:
            o.inited = True
            o.mm = mm
        else:
            o = cls.loads(uid, redis_data, o=o)
            o.inited = False
            o.mm = mm

            cls.run_data_version_update(_key, o)

        if settings.DEBUG:
            print 'model get: %s, status: %s' % (_key, o.inited)

        return o

    def reset(self, save=True):
        """重置数据
        """
        self.__dict__.update(self._attrs)
        if save:
            self.save()

    def reload(self):
        """重新加载数据
        """
        self.__dict__.updata(self.get(self.uid).__dict__)

    def delete(self):
        """删除数据
        """
        _key = self._model_key
        self.redis.delete(_key)

    def pre_init(self):
        """模块使用前预初始化方法, 在挂在 get 函数之内调用
        """
        pass

    def pre_use(self):
        """模块使用前预处理方法, 在挂在 mm 之后调用
        """
        pass