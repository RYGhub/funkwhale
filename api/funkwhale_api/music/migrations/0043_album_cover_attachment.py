# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_attachments(apps, schema_editor):
    Album = apps.get_model("music", "Album")
    Attachment = apps.get_model("common", "Attachment")

    album_attachment_mapping = {}
    def get_mimetype(path):
        if path.lower().endswith('.png'):
            return "image/png"
        return "image/jpeg"
    qs = Album.objects.filter(attachment_cover=None).exclude(cover="").exclude(cover=None)
    total = qs.count()
    print('Creating attachments for {} album covers, this may take a while…'.format(total))
    from django.core.files.storage import FileSystemStorage
    for i, album in enumerate(qs):
        if isinstance(album.cover.storage._wrapped, FileSystemStorage):
            try:
                size = album.cover.size
            except FileNotFoundError:
                # can occur when file isn't found on disk or S3
                print("  Warning: cover file wasn't found in storage: {}".format(e.__class__))
                size = None
        album_attachment_mapping[album] = Attachment(
            file=album.cover,
            size=None,
            mimetype=get_mimetype(album.cover.name),
        )
    print('Commiting changes…')
    Attachment.objects.bulk_create(album_attachment_mapping.values(), batch_size=2000)
    # map each attachment to the corresponding album
    # and bulk save
    for album, attachment in album_attachment_mapping.items():
        album.attachment_cover = attachment

    Album.objects.bulk_update(album_attachment_mapping.keys(), fields=['attachment_cover'], batch_size=2000)


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0042_album_attachment_cover")]

    operations = [migrations.RunPython(create_attachments, rewind)]
