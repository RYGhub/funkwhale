from funkwhale_api.taskapp import celery
from funkwhale_api.providers.acoustid import get_acoustid_client

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


@celery.app.task(name='ImportJob.run', bind=True)
@celery.require_instance(models.ImportJob, 'import_job')
def import_job_run(self, import_job, replace=False):
    try:
        track, created = models.Track.get_or_create_from_api(mbid=import_job.mbid)
        track_file = None
        if replace:
            track_file = track.files.first()
        elif track.files.count() > 0:
            return

        track_file = track_file or models.TrackFile(
            track=track, source=import_job.source)
        track_file.download_file()
        track_file.save()
        import_job.status = 'finished'
        import_job.track_file = track_file
        import_job.save()
        return track.pk

    except Exception as exc:
        if not settings.DEBUG:
            raise import_job_run.retry(args=[self], exc=exc, countdown=30, max_retries=3)
        raise


@celery.app.task(name='Lyrics.fetch_content')
@celery.require_instance(models.Lyrics, 'lyrics')
def fetch_content(lyrics):
    html = lyrics_utils._get_html(lyrics.url)
    content = lyrics_utils.extract_content(html)
    cleaned_content = lyrics_utils.clean_content(content)
    lyrics.content = cleaned_content
    lyrics.save(update_fields=['content'])
