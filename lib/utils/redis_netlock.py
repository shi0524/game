# -*- coding: utf-8 –*-

"""
利用上下文管理器和redis创建锁
"""

import time


def acquire_lock(key, client, ex, retry):
    """ 获取锁的状态
    :param key: 锁相关的key
    :param client: redis链接实例
    :param ex: 锁的过期时间
    :param retry: 是否重试 如果是int型, 代表重试次数
    :return:
    """
    while 1:
        lock = client.setnx(key, 1)
        if lock:
            client.expire(key, ex)
            return True
        else:
            if not retry:
                return False
            if isinstance(retry, int):
                retry -= 1
            time.sleep(0.03)
    return False


def release_lock(key, client):
    """ 释放锁
    """
    client.delete(key)


def check_lock(cls, key, client):
    """ 查看是否锁是否还存在
    """
    if client.get(key):
        return True
    else:
        return False


class MyRedisLock(object):
    """利用上下文管理器创建锁类
    """
    def __init__(self, key, client, ex=1, retry=True):
        self._key = key
        self.client = client
        self.ex = ex
        self.retry = retry
        self.lock = True

    def __enter__(self):
        self.lock = acquire_lock(self._key, self.client, self.ex, self.retry)
        return self.lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            release_lock(self._key, self.client)


if __name__ == "__main__":
    import redis
    client = redis.Redis(connection_pool=redis.BlockingConnectionPool(max_connections=15, host='localhost', port=6379))
    lock = MyRedisLock('test_key', client, ex=1, retry=False)

    def lock_func(lock):

        with lock as f:
            if not f:
                rc, data = 1, {}
            else:
                rc, data = 0, {}
            return rc, data


