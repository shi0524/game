# -*- coding: utf-8 –*-

from lib.core.environ import ModelManager


class TaskEventBase(object):
    """
    """
    pass


class TaskEventDispatch(object):

    _models = []

    def __init__(self, *args, **kwargs):
        self.mm = None

    @classmethod
    def register_model(cls, model_name, model_class):
        """
        :param model_name:
        :param model_class:
        :return:
        """
        if model_name not in cls._models:
            cls._models.append((model_name, model_class))

    def call_method(self, method_name, *args, **kwargs):
        """
        :param method_name:
        :param args:
        :param kwargs:
        :return:
        """

        for model_name, model_class in self._models:
            if method_name not in model_class.__dict__:
                continue

            model = getattr(self.mm, model_name, None)
            if not model:
                model = model_class(self.mm)

            # 检查是否可以执行method_name
            check_execute_func = getattr(model_class, 'check_execute', None)
            if check_execute_func and not check_execute_func(self.mm):
                continue

            method = getattr(model, model_name, None)
            if method:
                method(*args, **kwargs)


ModelManager.register_events('task_event_dispatch', TaskEventDispatch)

