# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-15 09:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sereports', '0002_auto_20170704_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilebabyFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f', models.FileField(upload_to='.')),
                ('md5', models.CharField(max_length=32)),
            ],
        ),
    ]
