# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0002_auto_20151215_1645")]

    operations = [
        migrations.AlterField(
            model_name="album", name="release_date", field=models.DateField(null=True)
        )
    ]
