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


def checked_message(message):
    replaced_words = 'foo', 'bar'
    for word in replaced_words:
        message = re.sub(r"\b" + re.escape(word) + r"\b", 'CENCORED', message)
    message = re.sub(r'\bhttp://(?!example.com).+\b', 'CENCORED', message)
    return message


def htmlmessage(sqlmessage):
    return '<b>{0}</b>:{1}'.format(sqlmessage.username, sqlmessage.text)


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    '''
    Received messages from page, takes username form session, writes messages to db and
    returns them in html format to page
    '''

    def open(self, room_name):
        try:
            self.room = models.Room.objects.filter(name=room_name).get()
        except models.Room.DoesNotExist:
            self.close()

        session_engine = import_module(django.conf.settings.SESSION_ENGINE)
        session_key = self.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)
        if session_username_key(room_name) in session:
            self.username = session[session_username_key(room_name)]
        else:
            self.close()
            return

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        text = checked_message(parsed['text'])
        sqlmessage = models.Message(room=self.room, username=self.username, text=text)
        sqlmessage.save()
        self.write_message(htmlmessage(sqlmessage))


class UpdateWebSocket(tornado.websocket.WebSocketHandler):
    '''
    Received messages from page, takes username form session, writes messages to db and
    returns them in html format to page
    '''

    def open(self, room_name):
        try:
            self.room = models.Room.objects.filter(name=room_name).get()
        except models.Room.DoesNotExist:
            self.close()

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        messages_count = parsed['messages_count']
        sqlmessages = models.Message.objects.filter(room=self.room).all()
        htmlmessages = [htmlmessage(message) for message in sqlmessages[messages_count:]]

        json = tornado.escape.json_encode({'new_messages': htmlmessages})
        self.write_message(json)
