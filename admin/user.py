# -*- coding: utf-8 –*-

from admin import render
from lib.core.environ import ModelManager
from admin.decorators import require_permission


@require_permission
def select(req, **kwargs):
    """
    :param req:
    :param kwargs:
    :return:
    """
    ignore_reset_module = ('server_config',)

    uid = req.get_argument('uid', '')
    result = {'mm': None, 'user': None, 'uid': uid, 'msg': ''}
    result.update(kwargs)
    if uid:
        mm = ModelManager(uid)
        result['mm'] = mm
        result['user'] = mm.user
        result['ignore_reset_module'] = ignore_reset_module

    return render(req, 'admin/user/index.html', **result)

