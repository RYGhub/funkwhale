# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('music', '0012_auto_20161122_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('is_public', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='playlists')),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('position', models.PositiveIntegerField(db_index=True, editable=False)),
                ('playlist', models.ForeignKey(to='playlists.Playlist', related_name='playlist_tracks')),
                ('previous', mptt.fields.TreeOneToOneField(null=True, to='playlists.PlaylistTrack', related_name='next', blank=True)),
                ('track', models.ForeignKey(to='music.Track', related_name='playlist_tracks')),
            ],
            options={
                'ordering': ('-playlist', 'position'),
            },
        ),
    ]
