# -*- coding: utf-8 –*-

import os
import time
import settings
from datetime import timedelta
from celery.schedules import crontab

redis_config = settings.CELERY_CACHE
BROKER_URL = 'redis://:%s@%s:%s/%d' % (
    redis_config.get('password', ''), redis_config.get('host', ''),
    redis_config.get('port', 6300), redis_config.get('db', 0)
)
CELERY_RESULT_PERSISTENT = False
CELERY_RESULT_BACKEND = 'rpc://'

CELERY_RESULT_SERIALIZER = 'json'           # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24   # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显

# Timezone
CELERY_TIMEZONE='Asia/Shanghai'    # 指定时区，不指定默认为 'UTC'
# CELERY_TIMEZONE='UTC'

# import
CELERY_IMPORTS = (
    'celery_app.tasks',
)

CELERYD_CONCURRENCY = 1


def change_concurrency(num):
    """ celery worker 并发数
    """
    globals()['CELERYD_CONCURRENCY'] = num

schdule_logs_path = os.path.join(settings.BASE_ROOT, 'logs/cw_logs')
if not os.path.exists(schdule_logs_path):
    os.makedirs(schdule_logs_path)
CELERYD_LOG_FILE = os.path.join(schdule_logs_path, 'cw_%s_%s' % (str(settings.CW_NUM), time.strftime("%Y%m%d")))
CELERY_DEFAULT_QUEUE = 'celery'


# TODO 定时任务的使用(目前不会使用)
# schedules
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
         'task': 'tasks.add',
         'schedule': timedelta(seconds=30),       # 每 30 秒执行一次
         'args': (0, 1)                           # 任务函数参数
    },
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(hour=12, minute=9, day_of_week=3),
        'args': (16, 16),
    },
}
