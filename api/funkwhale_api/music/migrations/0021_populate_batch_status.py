# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_status(apps, schema_editor):
    from funkwhale_api.music.utils import compute_status

    ImportBatch = apps.get_model("music", "ImportBatch")

    for ib in ImportBatch.objects.prefetch_related("jobs"):
        ib.status = compute_status(ib.jobs.all())
        ib.save(update_fields=["status"])


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0020_importbatch_status")]

    operations = [migrations.RunPython(populate_status, rewind)]
