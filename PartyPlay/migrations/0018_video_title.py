# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-27 02:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PartyPlay', '0017_auto_20170926_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='title',
            field=models.CharField(default='default title set in Model', max_length=200),
        ),
    ]
