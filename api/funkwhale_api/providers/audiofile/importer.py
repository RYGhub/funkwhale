import os
import datetime
from django.core.files import File

from funkwhale_api.taskapp import celery
from funkwhale_api.music import models, metadata


@celery.app.task(name='audiofile.from_path')
def from_path(path):
    data = metadata.Metadata(path)

    artist = models.Artist.objects.get_or_create(
        name__iexact=data.get('artist'),
        defaults={'name': data.get('artist')},
    )[0]

    release_date = None
    try:
        year, month, day = data.get('date', None).split('-')
        release_date = datetime.date(
            int(year), int(month), int(day)
        )
    except (ValueError, TypeError):
        pass

    album = models.Album.objects.get_or_create(
        title__iexact=data.get('album'),
        artist=artist,
        defaults={
            'title': data.get('album'),
            'release_date': release_date,
        },
    )[0]

    position = None
    try:
        position = int(data.get('tracknumber', None))
    except ValueError:
        pass
    track = models.Track.objects.get_or_create(
        title__iexact=data.get('title'),
        album=album,
        defaults={
            'title': data.get('title'),
            'position': position,
        },
    )[0]

    if track.files.count() > 0:
        raise ValueError('File already exists for track {}'.format(track.pk))

    track_file = models.TrackFile(track=track)
    track_file.audio_file.save(
        os.path.basename(path),
        File(open(path, 'rb'))
    )
    track_file.save()

    return track_file
