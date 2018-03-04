from django.core.files.base import ContentFile

from funkwhale_api.taskapp import celery
from funkwhale_api.providers.acoustid import get_acoustid_client
from funkwhale_api.providers.audiofile.tasks import import_track_data_from_path

from django.conf import settings
from . import models
from . import lyrics as lyrics_utils


@celery.app.task(name='acoustid.set_on_track_file')
@celery.require_instance(models.TrackFile, 'track_file')
def set_acoustid_on_track_file(track_file):
    client = get_acoustid_client()
    result = client.get_best_match(track_file.audio_file.path)

    def update(id):
        track_file.acoustid_track_id = id
        track_file.save(update_fields=['acoustid_track_id'])
        return id
    if result:
        return update(result['id'])


def _do_import(import_job, replace):
    from_file = bool(import_job.audio_file)
    mbid = import_job.mbid
    acoustid_track_id = None
    duration = None
    track = None
    if not mbid and from_file:
        # we try to deduce mbid from acoustid
        client = get_acoustid_client()
        match = client.get_best_match(import_job.audio_file.path)
        if match:
            duration = match['recordings'][0]['duration']
            mbid = match['recordings'][0]['id']
            acoustid_track_id = match['id']
    if mbid:
        track, _ = models.Track.get_or_create_from_api(mbid=mbid)
    else:
        track = import_track_data_from_path(import_job.audio_file.path)

    track_file = None
    if replace:
        track_file = track.files.first()
    elif track.files.count() > 0:
        if import_job.audio_file:
            import_job.audio_file.delete()
        import_job.status = 'skipped'
        import_job.save()
        return

    track_file = track_file or models.TrackFile(
        track=track, source=import_job.source)
    track_file.acoustid_track_id = acoustid_track_id
    if from_file:
        track_file.audio_file = ContentFile(import_job.audio_file.read())
        track_file.audio_file.name = import_job.audio_file.name
        track_file.duration = duration
    else:
        track_file.download_file()
    track_file.save()
    import_job.status = 'finished'
    import_job.track_file = track_file
    if import_job.audio_file:
        # it's imported on the track, we don't need it anymore
        import_job.audio_file.delete()
    import_job.save()
    return track.pk


@celery.app.task(name='ImportJob.run', bind=True)
@celery.require_instance(
    models.ImportJob.objects.filter(
        status__in=['pending', 'errored']),
    'import_job')
def import_job_run(self, import_job, replace=False):
    def mark_errored():
        import_job.status = 'errored'
        import_job.save()

    try:
        return _do_import(import_job, replace)
    except Exception as exc:
        if not settings.DEBUG:
            try:
                self.retry(exc=exc, countdown=30, max_retries=3)
            except:
                mark_errored()
                raise
        mark_errored()
        raise


@celery.app.task(name='Lyrics.fetch_content')
@celery.require_instance(models.Lyrics, 'lyrics')
def fetch_content(lyrics):
    html = lyrics_utils._get_html(lyrics.url)
    content = lyrics_utils.extract_content(html)
    cleaned_content = lyrics_utils.clean_content(content)
    lyrics.content = cleaned_content
    lyrics.save(update_fields=['content'])
