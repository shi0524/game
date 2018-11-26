# -*- coding: utf-8 –*-


def test_ok(hm):
    """ 测试请求成功
    """
    return 0, {
        'status': 'ok',
    }


def test_error(hm):
    """ 测试报错
    :param hm:
    :return:
    """
    1 / 0
    return 0, {}