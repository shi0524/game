# -*- coding: utf-8 –*-

import time
import datetime

from lib.db import ModelTools
from lib.utils.zip_data import data_encode, data_decode


class Logging(ModelTools):

    EXPIRE_DAY = 7
    EXPIRE = 3600 * 24 * EXPIRE_DAY
    LAST_API_EXPIRE = 1800

    def __init__(self, uid='', server='', *args, **kwargs):
        super(Logging, self).__init__()
        self.uid = uid
        self.server_name = uid[:-7]
        self.redis = self.get_redis_client(self.server_name)
        self.today_index = self.make_key_cls('%s_%s' % (self.uid, time.strftime('%F')), self.server_name)

    def add_logging(self, method, args=None, data=None):
        """添加玩家动作记录
        args:
            method:
            args: 请求参数
            data: 结果
        """
        _key = self.make_key_cls('%s_%s' % (self.uid, time.time()), self.server_name)
        result = {'method': method, 'args': args or {}, 'data': data or {}, 'dt': time.strftime('%F %T')}
        s = data_encode(result)
        self.redis.set(_key, s)
        self.redis.expire(_key, self.EXPIRE)

        self.redis.rpush(self.today_index, _key)
        self.redis.expire(self.today_index, self.EXPIRE)

    def get_all_logging(self):
        data = []
        now = datetime.datetime.now()
        for i in [(now - datetime.timedelta(days=i)).isoformat()[:10] for i in xrange(0, self.EXPIRE_DAY)]:
            index = self.make_key_cls('%s_%s' % (self.uid, i), self.server_name)
            for _key in self.redis.lrange(index, 0, -1)[::-1]:
                d = self.redis.get(_key)
                if d:
                    data.append(data_decode(d))
        return data

    def get_one_day_logging(self, days_str):
        """ 获取一天的日志

        :param days_str: '2016-01-26'
        :return:
        """
        data = []
        index = self.make_key_cls('%s_%s' % (self.uid, days_str), self.server_name)
        for _key in self.redis.lrange(index, 0, -1)[::-1]:
            d = self.redis.get(_key)
            if d:
                data.append(data_decode(d))
        return data

    def get_some_logging(self, days):
        """ 获得玩家最近 days(int) 天数的日志, days最大等于7 """

        if days > 7 or days <= 0 or type(days) != int:
            days = 7

        data = []
        now = datetime.datetime.now()
        # 获得格式如 "2015-03-02" 的日期列表
        date_list = [(now - datetime.timedelta(days=i)).isoformat()[:10] for \
                      i in xrange(0, days)]

        for date in date_list:
            raw_str = '%s_%s' % (self.uid, date)
            index = self.make_key_cls(raw_str, self.server_name)
            for _key in self.redis.lrange(index, 0, -1)[::-1]:
                d = self.redis.get(_key)
                if d:
                    data.append(data_decode(d))
        return data

    def get_last_api_key(self):
        _key = self.make_key_cls('%s_%s' % (self.uid, '_last_api'), self.server_name)
        return _key

    def add_last_api_data(self, method, output_data):
        """记录上个api请求的返回数据
        """
        _key = self.get_last_api_key()
        result = {'m': method, 'd': output_data}
        s = data_encode(result)
        self.redis.set(_key, s, ex=self.LAST_API_EXPIRE)

    def get_last_api_data(self):
        """获取最后一次api数据
        """
        data = {}
        _key = self.get_last_api_key()
        d = self.redis.get(_key)
        if d:
            data = data_decode(d)
        return data