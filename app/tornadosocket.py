import re
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")

import django.conf
from django.utils.importlib import import_module
import django.core.handlers.wsgi

import tornado.websocket
import tornado.escape

import app.models as models
from app.views import session_username_key

session_engine = import_module(django.conf.settings.SESSION_ENGINE)


def checked_message(message):
    replaced_words = 'foo', 'bar'
    for word in replaced_words:
        message = re.sub(r"\b" + re.escape(word) + r"\b", 'CENCORED', message)
    message = re.sub(r'\bhttp://(?!example.com).+\b', 'CENCORED', message)
    return message


class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def open(self, room_name):
        try:
            self.room = models.Room.objects.filter(name=room_name).get()
        except models.Room.DoesNotExist:
            self.close()
        # Can`t understand why this doesn`t work:(session_key is always None)
        # session_key = self.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
        # session = session_engine.SessionStore(session_key)
        # if session_username_key(room_name) in session:
        #     self.username = session[session_username_key(room_name)]
        # else:
        #     self.close()
        #     return

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        text = checked_message(parsed['text'])
        sqlmessage = models.Message(room=self.room, username=parsed['username'], text=text)
        sqlmessage.save()
        strmessage = '<b>{0}</b>:{1}'.format(sqlmessage.username, sqlmessage.text)
        self.write_message(strmessage)