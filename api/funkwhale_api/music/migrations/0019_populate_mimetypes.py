# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from funkwhale_api.music.utils import guess_mimetype


def populate_mimetype(apps, schema_editor):
    TrackFile = apps.get_model("music", "TrackFile")

    for tf in TrackFile.objects.filter(
        audio_file__isnull=False, mimetype__isnull=True
    ).only("audio_file"):
        try:
            tf.mimetype = guess_mimetype(tf.audio_file)
        except Exception as e:
            print("Error on track file {}: {}".format(tf.pk, e))
            continue
        print("Track file {}: {}".format(tf.pk, tf.mimetype))
        tf.save(update_fields=["mimetype"])


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0018_auto_20180218_1554")]

    operations = [migrations.RunPython(populate_mimetype, rewind)]
