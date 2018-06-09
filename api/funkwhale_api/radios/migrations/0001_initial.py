# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("music", "0004_track_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="RadioSession",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("radio_type", models.CharField(max_length=50)),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="radio_sessions",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RadioSessionTrack",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("position", models.IntegerField(default=1)),
                (
                    "session",
                    models.ForeignKey(
                        to="radios.RadioSession",
                        related_name="session_tracks",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "track",
                    models.ForeignKey(
                        to="music.Track",
                        related_name="radio_session_tracks",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ("session", "position")},
        ),
        migrations.AlterUniqueTogether(
            name="radiosessiontrack", unique_together=set([("session", "position")])
        ),
    ]
