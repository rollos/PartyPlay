import datetime
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User



class Room(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200, default='', primary_key=True)
    public = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    current_video = models.ForeignKey('Video', null=True, blank=True,  on_delete=models.SET_NULL, related_name='currently_playing')
    next_time = models.DateTimeField(null=True, blank=True)

    favorite_users = models.ManyToManyField(User, blank=True, related_name='favorite_users')
    pass

    def get_absolute_url(self):

        return reverse('room-detail-view', args=[str(self.url)])





    def __str__(self):
        return str(self.name)






class Video(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    videoID = models.CharField(max_length=200, default='0')
    title = models.CharField(max_length=200, default = 'default title set in Model')
    duration = models.DurationField(default=datetime.timedelta(seconds=30))
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='uploader_user')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    played = models.BooleanField(default = False)
    voters = models.ManyToManyField(User, related_name='vote_users', blank=True)

    pass

    def __str__(self):
        return str(self.videoID)

    def get_votes(self):
        return self.voters.all().count()


