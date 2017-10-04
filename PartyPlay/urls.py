from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.RoomModelListView.as_view(), name='rooms'),
    url(r'^addroom/$', login_required(views.RoomCreate.as_view()), name='add-room'),
    url(r'^(?P<pk>.+)/queue/$', views.get_queue, name='get-queue'),
    url(r'^(?P<pk>.+)/add/$', views.add_video, name='add-video'),
    url(r'^(?P<pk>.+)/video_end/$', views.video_end, name='end-video'),
    url(r'^(?P<pk>.+)/favorite/$', views.favorite_room, name='favorite-room'),
    url(r'^vote/$', views.upvote, name='vote'),
    url(r'^(?P<pk>.+)/$', views.RoomModelDetailView.as_view(), name='room-detail-view'),


]