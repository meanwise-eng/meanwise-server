# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-18 09:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userprofile', '0015_skill_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Influencer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userprofile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.UserProfile')),
            ],
        ),
    ]
