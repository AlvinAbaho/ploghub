# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 11:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ploghubapp', '0006_comment_historicalcomment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcomment',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalcomment',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='historicalcomment',
            name='post',
        ),
        migrations.RemoveField(
            model_name='historicalcomment',
            name='user',
        ),
        migrations.DeleteModel(
            name='HistoricalComment',
        ),
    ]