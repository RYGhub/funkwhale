# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_attachments(apps, schema_editor):
    Actor = apps.get_model("federation", "Actor")
    User = apps.get_model("users", "User")
    Attachment = apps.get_model("common", "Attachment")

    obj_attachment_mapping = {}
    def get_mimetype(path):
        if path.lower().endswith('.png'):
            return "image/png"
        return "image/jpeg"
    qs = User.objects.filter(actor__attachment_icon=None).exclude(avatar="").exclude(avatar=None).exclude(actor=None).select_related('actor')
    total = qs.count()
    print('Creating attachments for {} user avatars, this may take a while…'.format(total))
    from django.core.files.storage import FileSystemStorage
    for i, user in enumerate(qs):
        size = None
        if isinstance(user.avatar.storage._wrapped, FileSystemStorage):
            try:
                size = user.avatar.size
            except FileNotFoundError:
                # can occur when file isn't found on disk or S3
                print("  Warning: avatar file wasn't found in storage: {}".format(e.__class__))
        obj_attachment_mapping[user.actor] = Attachment(
            file=user.avatar,
            size=size,
            mimetype=get_mimetype(user.avatar.name),
        )
    print('Commiting changes…')
    Attachment.objects.bulk_create(obj_attachment_mapping.values(), batch_size=2000)
    # map each attachment to the corresponding obj
    # and bulk save
    for obj, attachment in obj_attachment_mapping.items():
        obj.attachment_icon = attachment

    Actor.objects.bulk_update(obj_attachment_mapping.keys(), fields=['attachment_icon'], batch_size=2000)


def rewind(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("users", "0016_auto_20190920_0857"), ("federation", "0024_actor_attachment_icon")]

    operations = [migrations.RunPython(create_attachments, rewind)]
