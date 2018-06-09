# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("radios", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="radiosession",
            name="session_key",
            field=models.CharField(null=True, blank=True, max_length=100),
        )
    ]
