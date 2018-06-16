# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
from django.db import migrations, models


def populate_uuids(apps, schema_editor):
    models = [
        "Album",
        "Artist",
        "Importbatch",
        "Importjob",
        "Lyrics",
        "Track",
        "Trackfile",
        "Work",
    ]
    for m in models:
        kls = apps.get_model("music", m)
        qs = kls.objects.filter(uuid__isnull=True).only("id")
        print("Setting uuids for {} ({} objects)".format(m, len(qs)))
        for o in qs:
            o.uuid = uuid.uuid4()
            o.save(update_fields=["uuid"])


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0023_auto_20180407_1010")]

    operations = [
        migrations.RunPython(populate_uuids, rewind),
        migrations.AlterField(
            model_name="album",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="artist",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="importbatch",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="importjob",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="lyrics",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="track",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="trackfile",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="work",
            name="uuid",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
    ]
