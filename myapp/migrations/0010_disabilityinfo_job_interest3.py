# Generated by Django 2.0.1 on 2018-03-05 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_auto_20180305_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='disabilityinfo',
            name='job_interest3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
