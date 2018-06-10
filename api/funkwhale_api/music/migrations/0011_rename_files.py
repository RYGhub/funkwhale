# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def rename_files(apps, schema_editor):
    """
    This migration script is utterly broken and made me redownload all my audio files.
    So next time -> Write some actual tests before running a migration script
    on thousand of tracks...
    """
    return
    # TrackFile = apps.get_model("music", "TrackFile")
    # qs = TrackFile.objects.select_related(
    #     'track__album__artist', 'track__artist')
    # total = len(qs)
    #
    #
    # for i, tf in enumerate(qs):
    #     try:
    #         new_name = '{} - {} - {}'.format(
    #             tf.track.artist.name,
    #             tf.track.album.title,
    #             tf.track.title,
    #         )
    #     except AttributeError:
    #         new_name = '{} - {}'.format(
    #             tf.track.artist.name,
    #             tf.track.title,
    #         )
    #     rename_file(
    #         instance=tf,
    #         field_name='audio_file',
    #         allow_missing_file=True,
    #         new_name=new_name)
    #     print('Renamed file {}/{} (new name: {})'.format(
    #         i + 1, total, tf.audio_file.name
    #     ))


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0010_auto_20160920_1742")]

    operations = [
        migrations.AlterField(
            model_name="trackfile",
            name="audio_file",
            field=models.FileField(upload_to="tracks/%Y/%m/%d", max_length=255),
        ),
        migrations.RunPython(rename_files, rewind),
    ]
