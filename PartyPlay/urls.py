from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.RoomModelListView.as_view(), name='rooms'),
    url(r'^(?P<pk>.+)/add/$', views.add_video, name='add-video'),
    url(r'^(?P<pk>.+)/video_end/$', views.video_end, name='end-video'),
    url(r'^vote/$', views.upvote, name='vote'),
    url(r'^(?P<pk>.+)/$', views.RoomModelDetailView.as_view(), name='room-detail-view'),

]