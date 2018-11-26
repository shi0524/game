# -*- coding: utf-8 –*-

import os
import types
import importlib
import settings

# 配置模板

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
_exclude_files = ['__init__']


def load():
    import gconfig

    if gconfig.CONFIG_TEMPLATES_STATUS:
        return
    gconfig.CONFIG_TEMPLATES_STATUS = True

    for _root, _dirs, _files in os.walk(CUR_PATH):
        for _f in _files:
            _name, _ext = os.path.splitext(_f)
            if _ext == '.py' and _name not in _exclude_files:
                module = importlib.import_module('gconfig.config_templates.%s' % _name)
                for func_name in dir(module):
                    if func_name.startswith('__'):
                        continue
                    func = getattr(module, func_name)
                    if isinstance(func, (types.DictionaryType, types.TupleType)):
                        if func_name in globals():
                            print 'config_templates %s repeat, name %s' % (func_name, _name)
                        globals()[func_name] = func
                        if func_name not in settings.CONFIG_NAME_LIST:
                            settings.CONFIG_NAME_LIST.append(func_name)

load()

