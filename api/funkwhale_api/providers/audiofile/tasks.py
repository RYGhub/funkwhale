import acoustid
import os
import datetime
from django.core.files import File
from django.db import transaction

from funkwhale_api.taskapp import celery
from funkwhale_api.providers.acoustid import get_acoustid_client
from funkwhale_api.music import models, metadata


@transaction.atomic
def import_track_data_from_path(path):
    data = metadata.Metadata(path)
    artist = models.Artist.objects.get_or_create(
        name__iexact=data.get('artist'),
        defaults={
            'name': data.get('artist'),
            'mbid': data.get('musicbrainz_artistid', None),
        },
    )[0]

    release_date = data.get('date', default=None)
    album = models.Album.objects.get_or_create(
        title__iexact=data.get('album'),
        artist=artist,
        defaults={
            'title': data.get('album'),
            'release_date': release_date,
            'mbid': data.get('musicbrainz_albumid', None),
        },
    )[0]

    position = data.get('track_number', default=None)
    track = models.Track.objects.get_or_create(
        title__iexact=data.get('title'),
        album=album,
        defaults={
            'title': data.get('title'),
            'position': position,
            'mbid': data.get('musicbrainz_recordingid', None),
        },
    )[0]
    return track


def import_metadata_with_musicbrainz(path):
    pass


@celery.app.task(name='audiofile.from_path')
def from_path(path):
    acoustid_track_id = None
    try:
        client = get_acoustid_client()
        result = client.get_best_match(path)
        acoustid_track_id = result['id']
    except acoustid.WebServiceError:
        track = import_track_data_from_path(path)
    except (TypeError, KeyError):
        track = import_metadata_without_musicbrainz(path)
    else:
        track, created = models.Track.get_or_create_from_api(
            mbid=result['recordings'][0]['id']
        )

    if track.files.count() > 0:
        raise ValueError('File already exists for track {}'.format(track.pk))

    track_file = models.TrackFile(
        track=track, acoustid_track_id=acoustid_track_id)
    track_file.audio_file.save(
        os.path.basename(path),
        File(open(path, 'rb'))
    )
    track_file.save()

    return track_file
