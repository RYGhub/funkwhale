# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0009_auto_20160920_1614")]

    operations = [
        migrations.AlterField(
            model_name="lyrics", name="url", field=models.URLField(unique=True)
        )
    ]
