# -*- coding: utf-8 –*-

import os

from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.httpserver import HTTPServer
import tornado

define('port', default=8888, help='run on the given port', type=int)
define('env', default='local', help='the env', type=str)
define('server_name', default='all')
define('numprocs', default='1', help='process sum', type=int)
define('debug', default=False, help='run at debug mode', type=bool)
define('maxmem', default=0, help='max memory use, overflow kill by self. (0 unlimit)', type=int)

options.parse_command_line()

import settings
settings.set_env(options.env, options.server_name)

from tornado.web import RequestHandler


class TestHandler(RequestHandler):
    def get(self):
        self.write("Hello, world!")


class Application(web.Application):
    def __init__(self, debug=False):
        handlers = [
            (r'/admin/([\w-]+)/?', 'admin.handler.AdminHandler'),
            (r"/admin/([\w-]+)/([\w-]+)/?", 'admin.handler.AdminHandler'),
            (r"/?[a-zA-Z0-9_]*/api/?", 'handlers.APIRequestHandler'),
        ]

        app_settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            static_url_prefix='/%s/static' % settings.URL_PARTITION,
            debug=debug,
        )

        super(Application, self).__init__(handlers, **app_settings)


def main_single():

    # tornado多进程模式不支持debug模式中的autoreload
    debug = options.debug if options.numprocs == 1 else False
    app = Application(debug)
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start()
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


def main():
    pass


if __name__ == '__main__':
    if options.numprocs == 1:
        main_single()
    else:
        main()
