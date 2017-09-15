from django.contrib import auth
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import generic
from django.views.generic.edit import FormMixin

from PartyPlay.forms import UploadVideoForm
from PartyPlay.models import Room, Video

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

class RoomModelListView(generic.ListView):
    model = Room
    context_object_name = 'room_list'
    template_name = 'partyplay/roommodel_list.html'


class RoomModelDetailView(generic.DetailView):
    model = Room
    context_object_name = 'room_data'
    template_name = 'partyplay/roommodel_detail.html'

    upload_form = UploadVideoForm




    def get_context_data(self, **kwargs):
        # Call the base implementation to get the original context
        context = super(RoomModelDetailView, self).get_context_data(**kwargs)

        # Get the songs currently in the room


        #Ugly ass shit to get the songs ordered by the amount of voters of the song
        top_songs = self.object.video_set.filter(played=False).annotate(votes_count=Count('voters')).order_by('-votes_count')[:11]

        context['current_videos'] = top_songs[1:]
        context['currently_playing'] = top_songs[0]


        if auth.user_logged_in:
            upvoted = []

            for video in top_songs:
                if video.voters.filter(pk=self.request.user.pk).exists():
                    upvoted.append(video)
            context['upvoted'] = upvoted


        context['upload_form'] = self.upload_form
        return context

@login_required
@require_http_methods(["POST"])
def add_video(request, pk):

    form = UploadVideoForm(request.POST)
    room = Room.objects.get(pk=pk)


    if form.is_valid():
        video = Video()
        video.uploader = auth.get_user(request)
        video.room = room
        video.video_name = form.cleaned_data['video_name']
        video.video_url = form.cleaned_data['video_url']
        video.save()

    return redirect(room.get_absolute_url())



@login_required
def vote(request, pk):
    video = Video.objects.get(pk=pk)
    user = auth.get_user(request)
    if user not in video.voters.all():
        video.voters.add(user)
    else:
        video.voters.remove(user)

    return redirect(video.room.get_absolute_url())








class UserProfilePage(LoginRequiredMixin, generic.ListView):
    model = Video
    template_name = 'partyplay/userprofile.html'


    def get_context_data(self, **kwargs):

        context = super(UserProfilePage, self).get_context_data(**kwargs)

        context['uploaded_videos'] = Video.objects.filter(uploader=self.request.user).order_by('-rank')
        context['created_rooms'] = Room.objects.filter(creator=self.request.user).all()

        return context