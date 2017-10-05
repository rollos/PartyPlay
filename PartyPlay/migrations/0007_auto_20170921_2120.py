# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-21 21:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PartyPlay', '0006_auto_20170915_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='currently_playing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='currently_playing', to='PartyPlay.Video'),
        ),
        migrations.AddField(
            model_name='room',
            name='next_time',
            field=models.DateTimeField(null=True),
        ),
    ]