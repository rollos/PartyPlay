import json


from django.core import serializers
from django.forms import model_to_dict
from django.template.loader import render_to_string


from datetime import date, timedelta
from .helper_functions import *
from django.contrib import auth
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
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

        context['queue'] = top_songs


        if self.object.next_time and self.object.next_time < timezone.now():
            update_currently_playing(self.object)

        context['current_video'] = self.object.current_video



        context['start_time'] = get_start_time(self.object)



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

    room = Room.objects.get(pk=pk)
    vid_id = request.POST.get('video_id')
    duration = request.POST.get('duration')
    title = request.POST.get('title')

    video = Video()
    video.uploader = auth.get_user(request)

    video.title = title
    video.duration = timedelta(seconds=int(duration))
    video.room = room
    video.videoID = vid_id
    video.save()


    return render_current_queue(request, video.room)


@require_http_methods(["POST"])
def video_end(request, pk):
    room = Room.objects.get(pk=pk)

    #Finished video pk
    str_val = request.POST.get("vid_pk")

    if request.user:
        user = request.user
    else:
        user = None


    #If there is no video on frontend
    if (str_val == '' or str_val == None):

        #If there is not a current video
        if room.current_video is None:
            new_pk = update_currently_playing(room)
        else:
            new_pk = room.current_video.pk

    #Thereis not a video playing
    else:
        vid_pk = int(str_val)

        #
        #find the first user to finish their video
        #This user's request will update current_video
        #Any subsequent requests will have different pk's than current_video,
        # they will only receive the updated data
        if room.current_video is None:
            new_pk = None
        elif room.current_video.pk == vid_pk:
            new_pk = update_currently_playing(room)
        else:
            new_pk = room.current_video.pk

    if room.current_video:
        current_vid = room.current_video.videoID
        current_vid_name = room.current_video.title
    else:
        current_vid = None
        current_vid_name = None


    t_u_n = get_time_until_next(room)

    context = {
        'current_video': room.current_video,

        'time_until_next': get_time_until_next(room),
        'queue': get_ordered_videos(room),
        'user': request.
    }


    response_data = {

        'html': render_to_string('partyplay/video_and_queue.html', context=context, request=request),
        'time_until_next': t_u_n,
        'current_vid_pk': new_pk,
        'current_vid_id': current_vid,
        'current_vid_name': current_vid_name,
        'start_time': get_start_time(room)
    }



    data = json.dumps(response_data)

    return HttpResponse(data, content_type='application.json')








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