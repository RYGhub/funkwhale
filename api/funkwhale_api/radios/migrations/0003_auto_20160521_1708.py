# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("radios", "0002_radiosession_session_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="radiosession",
            name="related_object_content_type",
            field=models.ForeignKey(
                null=True,
                to="contenttypes.ContentType",
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="radiosession",
            name="related_object_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
