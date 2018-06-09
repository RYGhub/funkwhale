# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("music", "0008_auto_20160529_1456"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Listening",
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
                (
                    "end_date",
                    models.DateTimeField(
                        null=True, blank=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "session_key",
                    models.CharField(null=True, blank=True, max_length=100),
                ),
                (
                    "track",
                    models.ForeignKey(
                        related_name="listenings",
                        to="music.Track",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        related_name="listenings",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ("-end_date",)},
        )
    ]
