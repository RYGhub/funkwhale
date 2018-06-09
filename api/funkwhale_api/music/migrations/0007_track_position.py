# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0006_unique_mbid")]

    operations = [
        migrations.AddField(
            model_name="track",
            name="position",
            field=models.PositiveIntegerField(blank=True, null=True),
        )
    ]
