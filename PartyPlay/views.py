import json


from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
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
from django.views.generic.edit import FormMixin, CreateView

from PartyPlay.forms import UploadVideoForm
from PartyPlay.models import Room, Video

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods





class RoomModelListView(generic.ListView):
    model = Room
    context_object_name = 'room_list'
    template_name = 'partyplay/roommodel_list.html'


    def get_context_data(self, **kwargs):
        context = super(RoomModelListView, self).get_context_data(**kwargs)
        favorite_room_list = []

        for room in context['room_list'].all():
            if self.request.user in room.favorite_users.all():
                favorite_room_list.append(room)


        context['favorite_room_list'] = favorite_room_list
        return context


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
    video.voters.add(request.user)
    video.save()


    return render_current_queue(request, video.room)


@login_required
@require_http_methods(["POST"])
def favorite_room(request, pk):
    room = Room.objects.get(pk=pk)

    if request.user in room.favorite_users.all():
        room.favorite_users.remove(request.user)
    else:
        room.favorite_users.add(request.user)

    return HttpResponse()


from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('rooms')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def get_queue(request, pk):
    room = Room.objects.get(pk=pk)
    return render_current_queue(request, room)


@require_http_methods(["POST"])
def video_end(request, pk):
    room = Room.objects.get(pk=pk)

    #Finished video pk
    str_val = request.POST.get("vid_pk")




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
        uploader = room.current_video.uploader.username
    else:
        current_vid = None
        current_vid_name = None
        uploader = None


    t_u_n = get_time_until_next(room)

    videos = get_ordered_videos(room)
    upvotes = []


    for video in videos:
        if request.user in video.voters.all():
            upvotes.append(video.pk)


    context = {
        'current_video': room.current_video,

        'time_until_next': get_time_until_next(room),
        'queue': get_ordered_videos(room),
        'upvotes': upvotes

    }


    response_data = {

        'html': render_to_string('partyplay/video_and_queue.html', context=context, request=request),
        'time_until_next': t_u_n,
        'current_vid_pk': new_pk,
        'current_vid_id': current_vid,
        'current_vid_name': current_vid_name,
        'current_uploader': uploader,
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

        context['uploaded_videos'] = Video.objects.filter(uploader=self.request.user)
        context['created_rooms'] = Room.objects.filter(creator=self.request.user).all()

        return context


class RoomCreate(CreateView):
    model = Room
    fields = ['name', 'public']
    template_name = 'partyplay/addroom.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.url = form.cleaned_data['name'].lower().replace(" ","")
        form.save()
        return super(RoomCreate, self).form_valid(form)



