from django import forms

from PartyPlay.models import Video


class UploadVideoForm(forms.Form):

    video_name = forms.CharField(label="Name")
    video_url = forms.CharField(label="URL")

