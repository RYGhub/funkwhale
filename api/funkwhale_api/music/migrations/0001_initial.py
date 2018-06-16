# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Album",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mbid", models.UUIDField(editable=False, blank=True, null=True)),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("title", models.CharField(max_length=255)),
                ("release_date", models.DateField()),
                (
                    "type",
                    models.CharField(
                        default="album", choices=[("album", "Album")], max_length=30
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Artist",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mbid", models.UUIDField(editable=False, blank=True, null=True)),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ImportBatch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        related_name="imports",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ImportJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source", models.URLField()),
                ("mbid", models.UUIDField(editable=False)),
                (
                    "status",
                    models.CharField(
                        default="pending",
                        choices=[("pending", "Pending"), ("finished", "finished")],
                        max_length=30,
                    ),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        related_name="jobs",
                        to="music.ImportBatch",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Track",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mbid", models.UUIDField(editable=False, blank=True, null=True)),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "album",
                    models.ForeignKey(
                        related_name="tracks",
                        blank=True,
                        null=True,
                        to="music.Album",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "artist",
                    models.ForeignKey(
                        related_name="tracks",
                        to="music.Artist",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="TrackFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("audio_file", models.FileField(upload_to="tracks")),
                ("source", models.URLField(blank=True, null=True)),
                ("duration", models.IntegerField(blank=True, null=True)),
                (
                    "track",
                    models.ForeignKey(
                        related_name="files", to="music.Track", on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="album",
            name="artist",
            field=models.ForeignKey(
                related_name="albums", to="music.Artist", on_delete=models.CASCADE
            ),
        ),
    ]
