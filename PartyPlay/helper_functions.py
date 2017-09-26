#Ugly ass shit to get the songs ordered by the amount of voters of the song
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render


def get_ordered_videos(room):
    return room.video_set.filter(played=False).annotate(votes_count=Count('voters')).order_by('-votes_count')




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
    return HttpResponse(render_to_string('partyplay/queue_body.html', context={'queue': get_ordered_videos(room)}, request=request))


def get_time_until_next(room):
    next_time = timezone.localtime(room.next_time)
    now = timezone.localtime(timezone.now())
    difference = next_time - now

    return int(difference.seconds) * 1000