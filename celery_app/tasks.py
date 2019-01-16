# -*- coding: utf-8 –*-

import time
from celery_app import app


"""
异步任务代码中两种使用举例
if settings.CELERY_SWITCH:
    server = "s1"
    r = random.randint(0, 1)
    if r:
        add.delay(1, 2, 1, xy=1.2)
    else:
        add.apply_async(args=[1, 2, 3], kwargs={"xy":2}, queue=which_queue(server))
else:
    add(1, 2)

"""


@app.task
def add(x, y, z=3, xy=1):
    time.sleep(0.1)
    return (x + y + z) * xy
