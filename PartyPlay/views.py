from django.shortcuts import render

# Create your views here.
from django.views import generic

from PartyPlay.models import Room, Video

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User


class RoomModelListView(generic.ListView):
    model = Room
    context_object_name = 'room_list'
    template_name = 'partyplay/roommodel_list.html'


class RoomModelDetailView(generic.DetailView):
    model = Room
    context_object_name = 'room_data'
    template_name = 'partyplay/roommodel_detail.html'


    def get_context_data(self, **kwargs):
        # Call the base implementation to get the original context
        context = super(RoomModelDetailView, self).get_context_data(**kwargs)

        # Get the songs currently in the room
        context['current_videos'] = self.object.video_set.filter(played=False).order_by('-rank')[:10]


        return context

class UserProfilePage(LoginRequiredMixin, generic.ListView):
    model = Video
    template_name = 'partyplay/userprofile.html'


    def get_context_data(self, **kwargs):

        context = super(UserProfilePage, self).get_context_data(**kwargs)

        context['uploaded_videos'] = Video.objects.filter(uploader=self.request.user).order_by('-rank')
        context['created_rooms'] = Room.objects.filter(creator=self.request.user).all()

        return context