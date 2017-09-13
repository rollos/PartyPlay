from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.RoomModelListView.as_view(), name='rooms'),
    url(r'^(?P<pk>.+)/$', views.RoomModelDetailView.as_view(), name='room-detail-view')
]