# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [("music", "0011_rename_files")]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="cover",
            field=versatileimagefield.fields.VersatileImageField(
                null=True, blank=True, upload_to="albums/covers/%Y/%m/%d"
            ),
        )
    ]
