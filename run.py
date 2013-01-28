import datetime
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")

import django.conf
import django.core.handlers.wsgi

from tornado.options import options, define
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

from app.tornadosocket import EchoWebSocket

define('port', type=int, default=8000)


class NoCacheStaticHandler(tornado.web.StaticFileHandler):
    """
    Request static file handlers for development and debug only.
    It disables any caching for static file.
    """
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', '0')
        now = datetime.datetime.now()
        expiration = datetime.datetime(now.year - 1, now.month, now.day)
        self.set_header('Last-Modified', expiration)


def run():
    wsgi_app = tornado.wsgi.WSGIContainer(
      django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application(
      [
        (r'/static/(.*)', NoCacheStaticHandler, {'path': 'chat/static'}),
        (r'/websocket/(.+)/', EchoWebSocket),
        (r'.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
      ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run()
