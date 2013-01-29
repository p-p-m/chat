from django.conf.urls import patterns, url

# from models import Room
# roomnames = Room.objects.value_list('name', flat=True)

urlpatterns = patterns('app.views',
    url(r'^about/$', 'about'),
    # url(r'^send_message_api/(?P<thread_id>\d+)/$', 'send_message_api_view'),
    # url(r'^chat/(?P<thread_id>\d+)/$', 'chat_view'),
    url(r'^$', 'main'),
    url(r'^rooms/(.+)/', 'room'),
    url(r'^login/(.+)/', 'login'),
    url(r'^delete/(.+)/(.+)', 'delete_user'),
)
