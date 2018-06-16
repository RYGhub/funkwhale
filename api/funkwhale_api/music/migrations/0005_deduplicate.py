# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def get_duplicates(model):
    return [
        i["mbid"]
        for i in model.objects.values("mbid")
        .annotate(idcount=models.Count("mbid"))
        .order_by("-idcount")
        if i["idcount"] > 1
    ]


def deduplicate(apps, schema_editor):
    Artist = apps.get_model("music", "Artist")
    Album = apps.get_model("music", "Album")
    Track = apps.get_model("music", "Track")

    for mbid in get_duplicates(Artist):
        ref = Artist.objects.filter(mbid=mbid).order_by("pk").first()
        duplicates = Artist.objects.filter(mbid=mbid).exclude(pk=ref.pk)
        Album.objects.filter(artist__in=duplicates).update(artist=ref)
        Track.objects.filter(artist__in=duplicates).update(artist=ref)
        duplicates.delete()

    for mbid in get_duplicates(Album):
        ref = Album.objects.filter(mbid=mbid).order_by("pk").first()
        duplicates = Album.objects.filter(mbid=mbid).exclude(pk=ref.pk)
        Track.objects.filter(album__in=duplicates).update(album=ref)
        duplicates.delete()


def rewind(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [("music", "0004_track_tags")]

    operations = [migrations.RunPython(deduplicate, rewind)]
