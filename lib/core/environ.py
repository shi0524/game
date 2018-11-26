# -*- coding: utf-8 –*-

import settings
import weakref


def func_type(value):
    try:
        return abs(int(value))
    except:
        return value


class HandlerManager(object):
    """ 请求管理类
    """

    _ARG_DEFAULT = []
    PARAMS_TYPE = (int, int)

    def __init__(self, request_handler):
        """
        :param request_handler:
        :return:
        """

        self.req = request_handler
        self.params = self.req.params
        self.get_arguments = self.req.get_arguments
        self.uid = self.req.get_argument('user_token', '')
        if not settings.check_uid(self.uid):
            self.uid = ''
        self.mm_class = ModelManager
        if self.uid:
            self.mm = ModelManager(self.uid, async_save=True)
            self.action = self.req.get_argument('method', '')
            self.args = self.params()
        else:
            self.mm = None

    def get_argument(self, name, default=_ARG_DEFAULT, is_int=False, strip=True):
        """ 获取参数
        :param name:
        :param default:
        :param is_int:
        :param strip:
        :return:
        """
        value = self.req.get_argument(name, default=default, strip=strip)
        if not value:
            return 0 if is_int else ''
        return abs(int(float(value))) if is_int else value

    def get_mapping_arguments(self, name, params_type=PARAMS_TYPE, split='_', result_type=list):
        """ 获取多个参数, 仅支持arg=1_1 或 arg=x_1&arg=y_1
        :param name: 参数名
        :param params_type: 参数默认类型
        :param split: 分隔符
        :param result_type: 返回类型 list, dict
        :return: [(1: 1), (1, 2)]
        """
        args = self.get_arguments(name)
        values = []
        num = len(params_type)
        func = lambda x: [v(x[k]) for k, v in enumerate(params_type)]
        for arg in args:
            arg_list = arg.split(split)
            if arg_list and len(arg_list) == num:
                if params_type:
                    values.append(func(arg_list))
                else:
                    values.append(arg_list)
        if not isinstance(values, result_type):
            values = result_type(values)
        return values

    def get_mapping_argument(self, name, is_int=True, num=2, split='_'):
        """ 获取参数, 仅支持arg=1_1 或 arg=1_1_2
        :param name: 参数名
        :param is_int: 是否值都为int
        :param num: 值的个数, 不支持1个
        :param split: 分隔符
        :return: [1, 2, 3]
        """
        arg_value = self.get_argument(name)
        values = []

        if not arg_value:
            return values

        arg_list = arg_value.split(split)
        arg_list = arg_list if arg_list else values

        if num and len(arg_list) != num:
            return values

        if is_int:
            return map(int, arg_list)
        return arg_list


class ModelManager(object):
    """ 管理类
    """
    _register_base = {}
    _register_base_tools = {}
    _register_base_iids = {}
    _register_events = {}

    def __init__(self, uid, async_save=False):
        self.uid = uid
        self.server = self.uid[:-7]         # 区服
        self.async_save = async_save
        self.action = ''
        self._mm = {}
        self.args = {}
        self._model = {}
        self._events = {}
        self._model_ids = {}
        self._model_tools = {}

    def get_model_key(self, model_name):
        return '%s_%s' % (self.uid, model_name)

    @classmethod
    def get_model_key_cls(cls, uid, model_name):
        return '%s_%s' % (uid, model_name)

    @classmethod
    def property_template(cls, model_name):
        doc = 'The %s property.' % model_name

        def fget(self):
            return self._get_obj(model_name)

        def fset(self, value):
            # key = '%s_%s' % (self.uid, model_name)
            key = self.get_model_key(model_name)
            self._model[key] = value

        def fdel(self):
            # key = '%s_%s' % (self.uid, model_name)
            key = self.get_model_key(model_name)
            del self._model[key]

        return {
            'doc': doc,
            'fget': fget,
            'fset': fset,
            'fdel': fdel,
        }

    @classmethod
    def register_model(cls, model_name, model):
        """ 注册 modelbase, 异步保存
        :param model_name: 类名
        :param model: 类
        :return:
        """
        from tools.task_event import TaskEventDispatch, TaskEventBase

        if model_name not in cls._register_base:
            cls._register_base[model_name] = model
            setattr(cls, model_name, property(**cls.property_template(model_name)))

            for base_class in model.__bases__:
                if issubclass(base_class, TaskEventBase):
                    TaskEventDispatch.register_model(model_name, model)
        else:
            old_model = cls._register_base[model_name]
            raise RuntimeError('model [%s] already exists \n'
                               'Conflict between the [%s] and [%s]' %
                               (model_name, old_model, model))

    @classmethod
    def register_model_base_tools(cls, model_name, model):
        """ 注册modeltools, 随时保存
        :param model_name:
        :param model:
        :return:
        """
        if model_name not in cls._register_base_tools:
            cls._register_base_tools[model_name] = model
        else:
            old_model = cls._register_base_tools[model_name]
            raise RuntimeError('model [%s] already exists \n'
                               'Conflict bettween the [%s] and [%s]' %
                               (model_name, old_model, model))

    @classmethod
    def register_model_iids(cls, model_name, model):
        """ 注册modelbase 或者别的父类, 随时保存
        :param model_name:
        :param model:
        :return:
        """
        if model_name not in cls._register_base_iids:
            cls._register_base_iids[model_name] = model
        else:
            old_model = cls._register_base_iids[model_name]
            raise RuntimeError('model [%s] already exists \n'
                               'Conflict bettween the [%s] and [%s]' %
                               (model_name, old_model, model))

    @classmethod
    def register_events(cls, model_name, model):
        """ 注册object, 异步保存
        :param model_name:
        :param model:
        :return:
        """
        if model not in cls._register_events:
            cls._register_events[model_name] = model
        else:
            old_model = cls._register_events[model_name]
            raise RuntimeError('model [%s] already exists \n'
                               'Conflict bettween the [%s] and [%s]' %
                               (model_name, old_model, model))

    def _get_obj(self, model_name):
        """ 获取model对象
        :param model_name:
        :return:
        """
        key = self.get_model_key(model_name)
        if key in self._model:
            obj = self._model[key]
        elif model_name in self._register_base:
            mm_proxy = weakref.proxy(self)
            obj = self._register_base[model_name].get(self.uid, self.server, mm=mm_proxy)
            obj.async_save = self.async_save
            obj._model_name = model_name
            setattr(obj, 'mm', mm_proxy)
            self._model[key] = obj
            if hasattr(obj, 'pre_use'):
                obj.pre_use()
        else:
            obj = None

        return obj

    def get_obj_tools(self, model, **kwargs):
        """ 获取model_tools对象
        :param model:
        :return:
        """
        key = self.get_model_key(model)
        if key in self._model_tools:
            obj = self._model_tools[key]
        elif model in self._register_base_tools:
            obj = self._register_base_tools[model](self.uid, self.server, **kwargs)
            setattr(obj, 'mm', weakref.proxy(self))
            self._model_tools[key] = obj
        else:
            obj = None

        return obj

    def get_obj_by_id(self, model, iid=''):
        """ 获取models对象, 区别于get_obj, 用于公共的数据, 如工会类
        :param model: 字符串 build
        :param iid: 代表models的key
        :return:
        """
        key = self.get_model_key_cls(iid, model)
        if key in self._model_ids:
            obj = self._model_ids[key]
        elif model in self._register_base_iids:
            mm_proxy = weakref.proxy(self)
            obj = self._register_base_iids[model].get(iid, self.server, mm=mm_proxy)
            setattr(obj, 'mm', mm_proxy)
            if hasattr(obj, 'pre_use'):
                obj.pre_use()
            self._model_ids[key] = obj
        else:
            obj = None

        return obj

    def get_mm(self, uid):
        """ 获取ModelManager对象
        :param uid:
        :return:
        """
        if self.uid == uid:
            return self
        if uid in self._mm:
            mm_obj = self._mm[uid]
        else:
            self._mm[uid] = mm_obj = self.__class__(uid, self.async_save)
        return mm_obj

    def get_event(self, model):
        """ 获取处理函数
        :param model:
        :return:
        """
        if model in self._events:
            obj = self._events[model]
        elif model in self._register_events:
            mm_proxy = weakref.proxy(self)
            obj = self._register_events[model](mm=mm_proxy)
            obj.async_save = self.async_save
            setattr(obj, 'mm', mm_proxy)
            self._events[model] = obj
        else:
            obj = None

        return obj

    def do_save(self, is_save=True):
        """ 保存对象信息, 仅支持self.get_obj中得到的对象
        :param is_save:
        :return:
        """
        if not is_save:
            return
        # 事件处理
        for event_obj in self._events.itervalues():
            if event_obj and hasattr(event_obj, 'handler'):
                event_obj.handler()

        for obj in self._model.itervalues():
            if settings.DEBUG:
                print 'ModelMananger.do_save', obj._model_key, getattr(obj, 'model_status', 0)
            if obj and getattr(obj, 'model_status', 0) == 1:
                obj._save()

        for mm_obj in self._mm.itervalues():
            mm_obj.do_save(is_save)

