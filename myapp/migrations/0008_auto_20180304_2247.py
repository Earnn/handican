# Generated by Django 2.0.1 on 2018-03-04 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_auto_20180304_1514'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='qualification',
        ),
        migrations.AddField(
            model_name='disabilityinfo',
            name='disability_level',
            field=models.CharField(blank=True, default='1', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='computer_skill1',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='computer_skill2',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='computer_skill3',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='disability_level',
            field=models.CharField(blank=True, default='1', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='language',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='level_computer_skill1',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='level_computer_skill2',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='level_computer_skill3',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='listen_skill',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='reading_skill',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='speaking_skill',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='working_time',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='writing_skill',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='disabilityinfo',
            name='current_status',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='detail',
            field=models.CharField(blank=True, default='ไม่ระบุ', max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='province',
            field=models.CharField(blank=True, default='', max_length=150, null=True),
        ),
    ]
