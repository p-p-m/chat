# coding: utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import models


def main(request):
    rooms_names = [room.name for room in models.Room.objects.all()]
    return render_to_response('main.html', {'rooms_names': rooms_names},
                                context_instance=RequestContext(request))


def about(request):
    return render_to_response('about.html')


def session_username_key(room_name):
    return 'user_' + room_name


def login(request, room_name):
    '''
    If user write correct username - saves it in session and into database and
    redirects to room view.
    '''
    try:
        sqlroom = models.Room.objects.filter(name=room_name).get()
    except models.Room.DoesNotExist:
        return HttpResponse("No such room.")
    room_usernames = models.ChatUser.objects.filter(room=sqlroom).values_list('name', flat=True)
    username_key = session_username_key(room_name)

    error = None
    if request.method == 'POST':
        new_username = request.POST['new_username']
        if not new_username:
            error = 'Error: empty username'
        if new_username in room_usernames:
            error = 'O_o we already have user with such name. Please choose another one...'
        if not error:
            request.session[username_key] = new_username
            return HttpResponseRedirect('/rooms/' + room_name)

    return render_to_response('login.html', {'error': error, 'room_usernames': room_usernames},
                            context_instance=RequestContext(request))


def room(request, room_name):
    '''
    Checks if user has username for room in session and
    if there isn`t any other unit with same name - openes chat page, otherwise - redirects to login.
    '''
    try:
        sqlroom = models.Room.objects.filter(name=room_name).get()
    except models.Room.DoesNotExist:
        return HttpResponse("No such room.")
    room_usernames = models.ChatUser.objects.filter(room=sqlroom).values_list('name', flat=True)

    if session_username_key(room_name) in request.session:
        messages = sqlroom.message_set.all()
        new_username = request.session[session_username_key(room_name)]
        if not new_username in room_usernames:
            chatuser = models.ChatUser(name=new_username, room=sqlroom)
            chatuser.save()
            return render_to_response('room.html', {'room_name': room_name, 'username': new_username,
                'messages': messages},
                 context_instance=RequestContext(request))

    return HttpResponseRedirect('/login/' + room_name)


def delete_user(request, room_name):
    '''
    Deletes user from base and session
    '''
    username_key = session_username_key(room_name)
    if username_key in request.session:
        username = request.session[username_key]
        user = models.ChatUser.objects.filter(name=username).get()
        user.delete()

    return HttpResponse("User delete page")
