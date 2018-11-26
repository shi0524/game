# -*- coding: utf-8 –*-

import settings


menu_name = [
    ('select', u'数据查询'),
    ('develop', u'开发工具'),
    ('adminlogs', u'日志记录'),
    ('manager', u'管理'),
]

select_sort = ['user', 'gwentcard', 'payment', 'long_connection', 'rank', 'user_name', 'other']
develop_sort = ['config', 'user']


menu_config = {
    'select': {
        'user': [{
            'name': u"用户数据",
            'sub': [
                ('select', u'用户查询', 1),
                ('update', u'用户修改', 0),
            ],
        }],
    },
    'develop': {
        'config': [{
            'name': u"配置",
            'sub': [
                ('select', u'配置首页', 1),
                ('upload', u'配置上传', 1),
                ('refresh', u'配置更新', 1)
            ],
        }],
    },
}