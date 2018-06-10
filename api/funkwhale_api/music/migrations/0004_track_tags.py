# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0002_auto_20150616_2121"),
        ("music", "0003_auto_20151222_2233"),
    ]

    operations = [
        migrations.AddField(
            model_name="track",
            name="tags",
            field=taggit.managers.TaggableManager(
                verbose_name="Tags",
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
            ),
        )
    ]
