# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-24 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_auto_20180124_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.Job'),
        ),
    ]