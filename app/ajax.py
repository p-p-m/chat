from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

import models
from views import session_username_key


@dajaxice_register(method='GET')
def delete_user(request, room_name):
    print 'deleting user from base', request.session[session_username_key(room_name)]
    username = request.session[session_username_key(room_name)]
    user = models.ChatUser.objects.filter(name=username).get()
    user.delete()
    return simplejson.dumps({'message': 'Hello World'})
