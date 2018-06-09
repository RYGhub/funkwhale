# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="album", options={"ordering": ["-creation_date"]}
        ),
        migrations.AlterModelOptions(
            name="artist", options={"ordering": ["-creation_date"]}
        ),
        migrations.AlterModelOptions(
            name="importbatch", options={"ordering": ["-creation_date"]}
        ),
        migrations.AlterModelOptions(
            name="track", options={"ordering": ["-creation_date"]}
        ),
        migrations.AddField(
            model_name="album",
            name="cover",
            field=models.ImageField(
                upload_to="albums/covers/%Y/%m/%d", null=True, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="trackfile",
            name="audio_file",
            field=models.FileField(upload_to="tracks/%Y/%m/%d"),
        ),
    ]
