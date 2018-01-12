# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-11 08:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('sex', models.CharField(max_length=10)),
                ('email', models.EmailField(max_length=100)),
                ('phone_no', models.CharField(default='-', max_length=20)),
                ('address', models.CharField(blank=True, default='-', max_length=1000, null=True)),
                ('disability_cate', models.CharField(max_length=100)),
                ('lastest_job', models.CharField(max_length=100)),
                ('lastest_office', models.CharField(max_length=100)),
                ('expected_salary', models.CharField(max_length=50)),
                ('expected_welfare', models.CharField(max_length=500)),
                ('talent', models.CharField(max_length=300)),
                ('talent2', models.CharField(max_length=300)),
                ('talent3', models.CharField(max_length=300)),
                ('more_resume', models.FileField(default='', upload_to='resume/')),
                ('get_more_info', models.BooleanField()),
                ('profile_picture', models.ImageField(default='', upload_to='profilePicture/')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
