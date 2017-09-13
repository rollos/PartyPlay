from django.db import models

# Create your models here.
from django.urls import reverse
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200, default=str(name), primary_key=True)
    public = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)




    def get_absolute_url(self):

        return reverse('room-detail-view', args=[str(self.id)])

    def __str__(self):
        return str(self.name)


class Video(models.Model):
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    video_url = models.CharField(max_length=2083)
    video_name = models.CharField(max_length=200)
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    rank = models.IntegerField(default=0)
    played = models.BooleanField(default = False)

    def __str__(self):
        return str(self.video_name)
