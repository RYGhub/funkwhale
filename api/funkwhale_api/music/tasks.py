import logging
import os

from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.dispatch import receiver

from musicbrainzngs import ResponseError
from requests.exceptions import RequestException

from funkwhale_api.common import channels
from funkwhale_api.common import preferences
from funkwhale_api.federation import activity, actors, routes
from funkwhale_api.federation import library as lb
from funkwhale_api.federation import library as federation_serializers
from funkwhale_api.providers.acoustid import get_acoustid_client
from funkwhale_api.taskapp import celery

from . import lyrics as lyrics_utils
from . import models
from . import metadata
from . import signals
from . import serializers

logger = logging.getLogger(__name__)


@celery.app.task(name="acoustid.set_on_upload")
@celery.require_instance(models.Upload, "upload")
def set_acoustid_on_upload(upload):
    client = get_acoustid_client()
    result = client.get_best_match(upload.audio_file.path)

    def update(id):
        upload.acoustid_track_id = id
        upload.save(update_fields=["acoustid_track_id"])
        return id

    if result:
        return update(result["id"])


def import_track_from_remote(metadata):
    try:
        track_mbid = metadata["recording"]["musicbrainz_id"]
        assert track_mbid  # for null/empty values
    except (KeyError, AssertionError):
        pass
    else:
        return models.Track.get_or_create_from_api(mbid=track_mbid)[0]

    try:
        album_mbid = metadata["release"]["musicbrainz_id"]
        assert album_mbid  # for null/empty values
    except (KeyError, AssertionError):
        pass
    else:
        album, _ = models.Album.get_or_create_from_api(mbid=album_mbid)
        return models.Track.get_or_create_from_title(
            metadata["title"], artist=album.artist, album=album
        )[0]

    try:
        artist_mbid = metadata["artist"]["musicbrainz_id"]
        assert artist_mbid  # for null/empty values
    except (KeyError, AssertionError):
        pass
    else:
        artist, _ = models.Artist.get_or_create_from_api(mbid=artist_mbid)
        album, _ = models.Album.get_or_create_from_title(
            metadata["album_title"], artist=artist
        )
        return models.Track.get_or_create_from_title(
            metadata["title"], artist=artist, album=album
        )[0]

    # worst case scenario, we have absolutely no way to link to a
    # musicbrainz resource, we rely on the name/titles
    artist, _ = models.Artist.get_or_create_from_name(metadata["artist_name"])
    album, _ = models.Album.get_or_create_from_title(
        metadata["album_title"], artist=artist
    )
    return models.Track.get_or_create_from_title(
        metadata["title"], artist=artist, album=album
    )[0]


def update_album_cover(album, upload, replace=False):
    if album.cover and not replace:
        return

    if upload:
        # maybe the file has a cover embedded?
        try:
            metadata = upload.get_metadata()
        except FileNotFoundError:
            metadata = None
        if metadata:
            cover = metadata.get_picture("cover_front")
            if cover:
                # best case scenario, cover is embedded in the track
                logger.info("[Album %s] Using cover embedded in file", album.pk)
                return album.get_image(data=cover)
        if upload.source and upload.source.startswith("file://"):
            # let's look for a cover in the same directory
            path = os.path.dirname(upload.source.replace("file://", "", 1))
            logger.info("[Album %s] scanning covers from %s", album.pk, path)
            cover = get_cover_from_fs(path)
            if cover:
                return album.get_image(data=cover)
    if not album.mbid:
        return
    try:
        logger.info(
            "[Album %s] Fetching cover from musicbrainz release %s",
            album.pk,
            str(album.mbid),
        )
        return album.get_image()
    except ResponseError as exc:
        logger.warning(
            "[Album %s] cannot fetch cover from musicbrainz: %s", album.pk, str(exc)
        )


IMAGE_TYPES = [("jpg", "image/jpeg"), ("png", "image/png")]


def get_cover_from_fs(dir_path):
    if os.path.exists(dir_path):
        for e, m in IMAGE_TYPES:
            cover_path = os.path.join(dir_path, "cover.{}".format(e))
            if not os.path.exists(cover_path):
                logger.debug("Cover %s does not exists", cover_path)
                continue
            with open(cover_path, "rb") as c:
                logger.info("Found cover at %s", cover_path)
                return {"mimetype": m, "content": c.read()}


@celery.app.task(name="Lyrics.fetch_content")
@celery.require_instance(models.Lyrics, "lyrics")
def fetch_content(lyrics):
    html = lyrics_utils._get_html(lyrics.url)
    content = lyrics_utils.extract_content(html)
    cleaned_content = lyrics_utils.clean_content(content)
    lyrics.content = cleaned_content
    lyrics.save(update_fields=["content"])


@celery.app.task(name="music.import_batch_notify_followers")
@celery.require_instance(
    models.ImportBatch.objects.filter(status="finished"), "import_batch"
)
def import_batch_notify_followers(import_batch):
    if not preferences.get("federation__enabled"):
        return

    if import_batch.source == "federation":
        return

    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    followers = library_actor.get_approved_followers()
    jobs = import_batch.jobs.filter(
        status="finished", library_track__isnull=True, upload__isnull=False
    ).select_related("upload__track__artist", "upload__track__album__artist")
    uploads = [job.upload for job in jobs]
    collection = federation_serializers.CollectionSerializer(
        {
            "actor": library_actor,
            "id": import_batch.get_federation_id(),
            "items": uploads,
            "item_serializer": federation_serializers.AudioSerializer,
        }
    ).data
    for f in followers:
        create = federation_serializers.ActivitySerializer(
            {
                "type": "Create",
                "id": collection["id"],
                "object": collection,
                "actor": library_actor.fid,
                "to": [f.url],
            }
        ).data

        activity.deliver(create, on_behalf_of=library_actor, to=[f.url])


@celery.app.task(
    name="music.start_library_scan",
    retry_backoff=60,
    max_retries=5,
    autoretry_for=[RequestException],
)
@celery.require_instance(
    models.LibraryScan.objects.select_related().filter(status="pending"), "library_scan"
)
def start_library_scan(library_scan):
    data = lb.get_library_data(library_scan.library.fid, actor=library_scan.actor)
    library_scan.modification_date = timezone.now()
    library_scan.status = "scanning"
    library_scan.total_files = data["totalItems"]
    library_scan.save(update_fields=["status", "modification_date", "total_files"])
    scan_library_page.delay(library_scan_id=library_scan.pk, page_url=data["first"])


@celery.app.task(
    name="music.scan_library_page",
    retry_backoff=60,
    max_retries=5,
    autoretry_for=[RequestException],
)
@celery.require_instance(
    models.LibraryScan.objects.select_related().filter(status="scanning"),
    "library_scan",
)
def scan_library_page(library_scan, page_url):
    data = lb.get_library_page(library_scan.library, page_url, library_scan.actor)
    uploads = []

    for item_serializer in data["items"]:
        upload = item_serializer.save(library=library_scan.library)
        if upload.import_status == "pending" and not upload.track:
            # this track is not matched to any musicbrainz or other musical
            # metadata
            import_upload.delay(upload_id=upload.pk)
        uploads.append(upload)

    library_scan.processed_files = F("processed_files") + len(uploads)
    library_scan.modification_date = timezone.now()
    update_fields = ["modification_date", "processed_files"]

    next_page = data.get("next")
    fetch_next = next_page and next_page != page_url

    if not fetch_next:
        update_fields.append("status")
        library_scan.status = "finished"
    library_scan.save(update_fields=update_fields)

    if fetch_next:
        scan_library_page.delay(library_scan_id=library_scan.pk, page_url=next_page)


def getter(data, *keys):
    if not data:
        return
    v = data
    for k in keys:
        v = v.get(k)

    return v


class UploadImportError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def fail_import(upload, error_code):
    old_status = upload.import_status
    upload.import_status = "errored"
    upload.import_details = {"error_code": error_code}
    upload.import_date = timezone.now()
    upload.save(update_fields=["import_details", "import_status", "import_date"])
    signals.upload_import_status_updated.send(
        old_status=old_status,
        new_status=upload.import_status,
        upload=upload,
        sender=None,
    )


@celery.app.task(name="music.import_upload")
@celery.require_instance(
    models.Upload.objects.filter(import_status="pending").select_related(
        "library__actor__user"
    ),
    "upload",
)
def import_upload(upload):
    data = upload.import_metadata or {}
    old_status = upload.import_status
    try:
        track = get_track_from_import_metadata(upload.import_metadata or {})
        if not track and upload.audio_file:
            # easy ways did not work. Now we have to be smart and use
            # metadata from the file itself if any
            track = import_track_data_from_file(upload.audio_file.file, hints=data)
        if not track and upload.metadata:
            # we can try to import using federation metadata
            track = import_track_from_remote(upload.metadata)
    except UploadImportError as e:
        return fail_import(upload, e.code)
    except Exception:
        fail_import(upload, "unknown_error")
        raise
    # under some situations, we want to skip the import (
    # for instance if the user already owns the files)
    owned_duplicates = get_owned_duplicates(upload, track)
    upload.track = track

    if owned_duplicates:
        upload.import_status = "skipped"
        upload.import_details = {
            "code": "already_imported_in_owned_libraries",
            "duplicates": list(owned_duplicates),
        }
        upload.import_date = timezone.now()
        upload.save(
            update_fields=["import_details", "import_status", "import_date", "track"]
        )
        signals.upload_import_status_updated.send(
            old_status=old_status,
            new_status=upload.import_status,
            upload=upload,
            sender=None,
        )
        return

    # all is good, let's finalize the import
    audio_data = upload.get_audio_data()
    if audio_data:
        upload.duration = audio_data["duration"]
        upload.size = audio_data["size"]
        upload.bitrate = audio_data["bitrate"]
    upload.import_status = "finished"
    upload.import_date = timezone.now()
    upload.save(
        update_fields=[
            "track",
            "import_status",
            "import_date",
            "size",
            "duration",
            "bitrate",
        ]
    )
    signals.upload_import_status_updated.send(
        old_status=old_status,
        new_status=upload.import_status,
        upload=upload,
        sender=None,
    )
    routes.outbox.dispatch(
        {"type": "Create", "object": {"type": "Audio"}}, context={"upload": upload}
    )
    if not track.album.cover:
        update_album_cover(track.album, upload)


def get_track_from_import_metadata(data):
    track_mbid = getter(data, "track", "mbid")
    track_uuid = getter(data, "track", "uuid")

    if track_mbid:
        # easiest case: there is a MBID provided in the import_metadata
        return models.Track.get_or_create_from_api(mbid=track_mbid)[0]
    if track_uuid:
        # another easy case, we have a reference to a uuid of a track that
        # already exists in our database
        try:
            return models.Track.objects.get(uuid=track_uuid)
        except models.Track.DoesNotExist:
            raise UploadImportError(code="track_uuid_not_found")


def get_owned_duplicates(upload, track):
    """
    Ensure we skip duplicate tracks to avoid wasting user/instance storage
    """
    owned_libraries = upload.library.actor.libraries.all()
    return (
        models.Upload.objects.filter(
            track__isnull=False, library__in=owned_libraries, track=track
        )
        .exclude(pk=upload.pk)
        .values_list("uuid", flat=True)
    )


@transaction.atomic
def import_track_data_from_file(file, hints={}):
    data = metadata.Metadata(file)
    album = None
    track_mbid = data.get("musicbrainz_recordingid", None)
    album_mbid = data.get("musicbrainz_albumid", None)

    if album_mbid and track_mbid:
        # to gain performance and avoid additional mb lookups,
        # we import from the release data, which is already cached
        return models.Track.get_or_create_from_release(album_mbid, track_mbid)[0]
    elif track_mbid:
        return models.Track.get_or_create_from_api(track_mbid)[0]
    elif album_mbid:
        album = models.Album.get_or_create_from_api(album_mbid)[0]

    artist = album.artist if album else None
    artist_mbid = data.get("musicbrainz_artistid", None)
    if not artist:
        if artist_mbid:
            artist = models.Artist.get_or_create_from_api(artist_mbid)[0]
        else:
            artist = models.Artist.objects.get_or_create(
                name__iexact=data.get("artist"), defaults={"name": data.get("artist")}
            )[0]

    release_date = data.get("date", default=None)
    if not album:
        album = models.Album.objects.get_or_create(
            title__iexact=data.get("album"),
            artist=artist,
            defaults={"title": data.get("album"), "release_date": release_date},
        )[0]
    position = data.get("track_number", default=None)
    track = models.Track.objects.get_or_create(
        title__iexact=data.get("title"),
        album=album,
        defaults={"title": data.get("title"), "position": position},
    )[0]
    return track


@receiver(signals.upload_import_status_updated)
def broadcast_import_status_update_to_owner(old_status, new_status, upload, **kwargs):
    user = upload.library.actor.get_user()
    if not user:
        return
    group = "user.{}.imports".format(user.pk)
    channels.group_send(
        group,
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "import.status_updated",
                "upload": serializers.UploadForOwnerSerializer(upload).data,
                "old_status": old_status,
                "new_status": new_status,
            },
        },
    )
