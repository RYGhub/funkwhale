# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0007_track_position")]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="mbid",
            field=models.UUIDField(null=True, db_index=True, unique=True, blank=True),
        ),
        migrations.AlterField(
            model_name="artist",
            name="mbid",
            field=models.UUIDField(null=True, db_index=True, unique=True, blank=True),
        ),
        migrations.AlterField(
            model_name="track",
            name="mbid",
            field=models.UUIDField(null=True, db_index=True, unique=True, blank=True),
        ),
    ]
