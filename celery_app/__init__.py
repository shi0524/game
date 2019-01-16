# -*- coding: utf-8 –*-

import settings
from celery import Celery


app = Celery('demo')
app.config_from_object('celery_app.celeryconfig')


def which_queue(server):
    server = settings.get_father_server(server)
    return 'celery_' + server
