# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("music", "0008_auto_20160529_1456")]

    operations = [
        migrations.CreateModel(
            name="Lyrics",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                ("url", models.URLField()),
                ("content", models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Work",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                (
                    "mbid",
                    models.UUIDField(unique=True, null=True, db_index=True, blank=True),
                ),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("language", models.CharField(max_length=20)),
                ("nature", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=255)),
            ],
            options={"ordering": ["-creation_date"], "abstract": False},
        ),
        migrations.AddField(
            model_name="lyrics",
            name="work",
            field=models.ForeignKey(
                related_name="lyrics",
                to="music.Work",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="track",
            name="work",
            field=models.ForeignKey(
                related_name="tracks",
                to="music.Work",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
    ]
