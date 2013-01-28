from django.db import models


class Room(models.Model):
    name = models.TextField()


class ChatUser(models.Model):
    name = models.TextField()
    room = models.ForeignKey(Room)


class Message(models.Model):
    text = models.TextField()
    username = models.TextField()
    room = models.ForeignKey(Room)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)
