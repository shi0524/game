# -*- coding: utf-8 –*-

import re
from tornado.web import RequestHandler
from tornado.util import unicode_type


class BaseRequestHandler(RequestHandler):
    """网络请求封装
    """
    def summary_params(self):
        """解析请求参数
        """
        return self.request.arguments

    @property
    def headers(self):
        """请求头
        """
        return self.request.headers

    @property
    def body(self):
        """请求体
        """
        return self.request.body

    def params(self, strip=True):
        data = {}
        for name, values in self.request.arguments.iteritems():
            vs = []
            for v in values:
                v = self.decode_argument(v, name=name)
                if isinstance(v, unicode_type):
                    v = RequestHandler._remove_control_chars_regex.sub(" ", v)
                if strip:
                    v = v.strip()
                vs.append(v)
            data[name] = vs[-1]
        return data

    def get_reg_params(self, reg_str, key_sort=int, value_sort=int, value_filter=None):
        """通过正则表达式获取参数和值, 返回[(key, value)]
        :param reg_str: 正则表达式
        :param key_sort: key的类型, 默认 int
        :param value_sort: value的类型, 默认 int
        :param value_filter: 是否筛选value值为0过滤掉参数
        """
        comp = re.compile(reg_str)
        p = []
        params = self.summary_params()
        for param_name, param_value in params.iteritems():
            for name in comp.findall(param_name):
                value = value_sort(param_name[0])
                if value != value_filter:
                    name = key_sort(name)
                    p.append((name, value))
        return p