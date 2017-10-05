from django import forms
from django.forms import ModelForm

from PartyPlay.models import Video


class UploadVideoForm(forms.Form):

    video_name = forms.CharField(label="Name")
    video_url = forms.CharField(label="URL")

from django.contrib.auth.models import User
