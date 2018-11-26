# -*- coding: utf-8 –*-


def require_permission(view_func):
    """
    装饰器，用于判断管理后台的帐号是否有权限访问
    """
    def wrapped_view_func(request, *args, **kwargs):

        result = view_func(request, *args, **kwargs)
        return result

    return wrapped_view_func