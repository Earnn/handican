# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-22 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_auto_20180122_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
