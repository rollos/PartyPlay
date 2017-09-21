import json

from django.contrib import auth
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import RequestContext
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormMixin

from PartyPlay.forms import UploadVideoForm
from PartyPlay.models import Room, Video

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


def render_current_queue(request, room):
    return render(request, 'partyplay/queue_body.html', {'current_videos': get_ordered_videos(room)})

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



        top_songs = get_ordered_videos(self.object)

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



#Ugly ass shit to get the songs ordered by the amount of voters of the song
def get_ordered_videos(room):
    return room.video_set.filter(played=False).annotate(votes_count=Count('voters')).order_by('-votes_count')

@login_required
@require_http_methods(["POST"])
def add_video(request, pk):

    room = Room.objects.get(pk=pk)
    name = request.POST.get('name')
    url = request.POST.get('url')

    video = Video()
    video.uploader = auth.get_user(request)
    video.room = room
    video.video_name = name
    video.video_url = url
    video.save()


    response_data = {}
    response_data['result'] = 'Create post successful!'
    response_data['postpk'] = video.pk
    response_data['text'] = video.video_name
    response_data['url'] = video.video_url
    response_data['author'] = video.uploader.username

    return render_current_queue(request, video.room)



@login_required
def upvote(request):
    context = RequestContext(request)
    pk = request.GET['vid_pk']
    video = get_object_or_404(Video, pk=pk)
    user = auth.get_user(request)
    if user not in video.voters.all():
        video.voters.add(user)
    else:
        video.voters.remove(user)

    video.save()

    return render_current_queue(request, video.room)




class UserProfilePage(LoginRequiredMixin, generic.ListView):
    model = Video
    template_name = 'partyplay/userprofile.html'


    def get_context_data(self, **kwargs):

        context = super(UserProfilePage, self).get_context_data(**kwargs)

        context['uploaded_videos'] = Video.objects.filter(uploader=self.request.user).order_by('-rank')
        context['created_rooms'] = Room.objects.filter(creator=self.request.user).all()

        return context