#Ugly ass shit to get the songs ordered by the amount of voters of the song
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render


def get_ordered_videos(room, user=None):


    return room.video_set.filter(played=False).annotate(votes_count=Count('voters')).order_by('-votes_count', 'date_uploaded')




def update_currently_playing(room):
    vids = get_ordered_videos(room)
    if vids:
        next_vid = vids[0] #Get the highest ranked video
        next_vid.played = True
        next_vid.save()

        room.next_time = timezone.localtime(timezone.now()) + next_vid.duration
        room.current_video = next_vid
        room.save()
        return next_vid.pk
    else:
        room.current_video = None
        room.next_time = None
        room.save()
        return None







def render_current_queue(request, room):
    videos = get_ordered_videos(room)
    upvotes = []

    for video in videos:

        if request.user in video.voters.all():
            upvotes.append(video.pk)


    return HttpResponse(render_to_string('partyplay/queue_body.html', context={'queue': get_ordered_videos(room), 'upvotes':upvotes}, request=request))


def get_time_until_next(room):

    next_time = timezone.localtime(room.next_time)
    now = timezone.localtime(timezone.now())



    difference = next_time - now

    return int(difference.seconds) * 1000

def get_start_time(room):
    time_until_next = get_time_until_next(room)
    tun = time_until_next

    time_until_seconds = time_until_next / 1000
    if room.current_video:

        duration = room.current_video.duration.seconds

        return duration - time_until_seconds
    else:
        return None