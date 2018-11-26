# -*- coding: utf-8 –*-

import hashlib


def md5(s):
    """
    :param s: 要MD5的数据
    :return: MD5值
    """
    return hashlib.md5(str(s)).hexdigest()


def add_dict(source, k, v):
    """ 合并字典(源字典值为int)
    :param source: 源字典 {k: v}
    :param k: 新增加的k
    :param v: 新增加的k的值
    :return:
    """
    if k in source:
        source[k] += v
    else:
        source[k] = v


def add_dict_list(source, k, v):
    """合并字典(源字典值为list)

    :param source: 源字典 {'k', v}
    :param k: 增加的k
    :param v: 增加k的值
    :return:
    """
    if k in source:
        source[k].append(v)
    else:
        source[k] = [v]