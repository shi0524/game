# -*- coding: utf-8 –*-

import tornado
import settings
import admin_config
from admin_models import Admin
from admin.decorators import require_permission


def render(req, tempalte_file, **kwargs):
    """
    :param req:
    :param tempalte:
    :param kwargs:
    :return:
    """
    kwargs['url_partition'] = settings.URL_PARTITION
    kwargs['PLATFORM'] = settings.PLATFORM
    kwargs['PRODUCT_NAME'] = settings.PRODUCT_NAME
    return tornado.web.RequestHandler.render(req, tempalte_file, **kwargs)


@require_permission
def index(req, *args, **kwargs):
    """首页
    :param req:
    :return:
    """
    return render(req, 'admin/main.html', **{})


@require_permission
def left(req, *args, **kwargs):
    """左侧栏
    :param req:
    :return:
    """
    return render(req, 'admin/left.html', **{})


@require_permission
def top(req, *args, **kwargs):
    """
    :param req:
    :return:
    """
    menu = req.get_argument('menu', 'select')
    return render(req, 'admin/info_view.html', **{'menu': menu})

@require_permission
def content(req, *args, **kwargs):
    """
    :param req:
    :return:
    """
    return render(req, 'admin/content.html')


@require_permission
def login(req):
    msgs = []
    d = {'msgs': msgs}
    if req.request.method == 'POST':
        username = req.get_argument('username', '')
        password = req.get_argument('password', '')
        if not username or not password:
            msgs.append(u'用户名或密码错误')
            return render(req, 'admin/login.html', **d)

        admin = Admin.get(username)
        if not admin:
            msgs.append(u'密码错误')
            return render(req, 'admin/login.html', **d)
        elif not admin.check_password(password):
            msgs.append(u'密码错误')
            return render(req, 'admin/login.html', **d)

        # auth.login(req, admin)
        return req.redirect('/%s/admin/index/' % settings.URL_PARTITION)
    return render(req, 'admin/login.html', **d)


def logout(req):
    """退出
    :param req:
    :return:
    """
    render(req, 'admin/login.html', **{'msgs': []})

