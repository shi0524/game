# -*- coding: utf-8 –*-

import os
import sys
import time
import openpyxl
import traceback
import settings
from admin import render
from models.config import Config
from gconfig import game_config
from gconfig.config_contents import mapping_config
from admin.decorators import require_permission


@require_permission
def select(req, **kwargs):
    """# config: docstring
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    config_key = req.get_argument('config_key', '')
    c = Config.get(config_key)
    config_data = c.value
    last_update_time = c.last_update_time

    if not config_data and config_key:
        config_data = getattr(game_config, config_key)

    refresh_text = req.get_argument('config_refresh_text', '')
    flag = int(req.get_argument('config_refresh_flag', 0))

    res_flag = int(req.get_argument('test_res_version_flag', -1))
    white_ip = req.get_argument('white_ip', '-1')

    version_dirs = os.path.join(settings.BASE_ROOT, 'logs', 'client_resource')

    msg = kwargs.get('msg', '')

    return render(req, 'admin/config/index.html', **{
        'mapping_config': mapping_config,
        'config_key': config_key,
        'config_data': config_data,
        'config_refresh_flag': 1,
        'config_refresh_text': refresh_text,
        'last_update_time': last_update_time,
        'test_res_version_flag': 1,  # resource.hot_update_switch,
        'can_hot_update_ip': 1,  # resource.can_hot_update_ip,
        'limit_version': 1,  # resource.limit_version,
        'recent_version': 1,  # resource.recent_version,
        'msg': msg,
    })


@require_permission
def upload(req):
    """

    :param req:
    :return:
    """
    file_obj = req.request.files.get('xls', None)

    if not file_obj:
        return select(req, msg=u"哥们，求文件")

    file_name = file_obj[0]['filename']
    platform = settings.PLATFORM
    if False and not settings.DEBUG and platform and platform not in file_name:
        return select(req, msg=u"检查配置文件是否为 %s 平台的" % platform)

    # 获取当前时分秒
    file_name_part = time.strftime('%Y-%m-%d-%H-%M-%S')

    # 保存文件
    file_dir = os.path.join(settings.BASE_ROOT, 'upload_xls')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    name, suffix = os.path.splitext(file_name)

    file_name = os.path.join(file_dir, '%s_%s%s' % (name, file_name_part, suffix))
    filebody = file_obj[0]['body']
    hfile = open(file_name, 'wb+')
    hfile.write(filebody)
    hfile.close()

    xl = openpyxl.load_workbook(filename=file_name, use_iterators=True)

    try:
        back_save_list, warning_msg = game_config.upload(file_name, xl)
    except:
        etype, value, tb = sys.exc_info()
        line = traceback.format_exception_only(etype, value)
        line_str = '-'.join(line)
        return select(req, **{'msg': 'back error: %s' % line_str.replace('\\', '')})

    if warning_msg:
        return select(req,  **{'msg': 'warning: %s, done: %s' % (','.join(warning_msg), ','.join(back_save_list))})
    return select(req, **{'msg': 'done: %s' % (','.join(back_save_list))})


@require_permission
def refresh(req):

    back_status = game_config.refresh()

    if back_status:
        return select(req, **{'msg': 'update success'})
    else:
        return select(req, **{'msg': 'no update'})