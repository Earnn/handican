# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-12 03:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_remove_companyinfo_company_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyinfo',
            name='user',
        ),
    ]
