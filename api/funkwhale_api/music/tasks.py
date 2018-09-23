import collections
import logging
import os

from django.utils import timezone
from django.db import transaction
from django.db.models import F, Q
from django.dispatch import receiver

from musicbrainzngs import ResponseError
from requests.exceptions import RequestException

from funkwhale_api.common import channels
from funkwhale_api.common import preferences
from funkwhale_api.federation import activity, actors, routes
from funkwhale_api.federation import library as lb
from funkwhale_api.federation import library as federation_serializers
from funkwhale_api.taskapp import celery

from . import lyrics as lyrics_utils
from . import models
from . import metadata
from . import signals
from . import serializers

logger = logging.getLogger(__name__)


def update_album_cover(album, source=None, cover_data=None, replace=False):
    if album.cover and not replace:
        return

    if cover_data:
        return album.get_image(data=cover_data)

    if source and source.startswith("file://"):
        # let's look for a cover in the same directory
        path = os.path.dirname(source.replace("file://", "", 1))
        logger.info("[Album %s] scanning covers from %s", album.pk, path)
        cover = get_cover_from_fs(path)
        if cover:
            return album.get_image(data=cover)
    if album.mbid:
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
            process_upload.delay(upload_id=upload.pk)
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


def getter(data, *keys, default=None):
    if not data:
        return default
    v = data
    for k in keys:
        try:
            v = v[k]
        except KeyError:
            return default

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

    broadcast = getter(
        upload.import_metadata, "funkwhale", "config", "broadcast", default=True
    )
    if broadcast:
        signals.upload_import_status_updated.send(
            old_status=old_status,
            new_status=upload.import_status,
            upload=upload,
            sender=None,
        )


@celery.app.task(name="music.process_upload")
@celery.require_instance(
    models.Upload.objects.filter(import_status="pending").select_related(
        "library__actor__user"
    ),
    "upload",
)
def process_upload(upload):
    import_metadata = upload.import_metadata or {}
    old_status = upload.import_status
    audio_file = upload.get_audio_file()
    try:
        additional_data = {}
        if not audio_file:
            # we can only rely on user proveded data
            final_metadata = import_metadata
        else:
            # we use user provided data and data from the file itself
            m = metadata.Metadata(audio_file)
            file_metadata = m.all()
            final_metadata = collections.ChainMap(
                additional_data, import_metadata, file_metadata
            )
            additional_data["cover_data"] = m.get_picture("cover_front")
        additional_data["upload_source"] = upload.source
        track = get_track_from_import_metadata(final_metadata)
    except UploadImportError as e:
        return fail_import(upload, e.code)
    except Exception:
        return fail_import(upload, "unknown_error")

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
    broadcast = getter(
        import_metadata, "funkwhale", "config", "broadcast", default=True
    )
    if broadcast:
        signals.upload_import_status_updated.send(
            old_status=old_status,
            new_status=upload.import_status,
            upload=upload,
            sender=None,
        )
    dispatch_outbox = getter(
        import_metadata, "funkwhale", "config", "dispatch_outbox", default=True
    )
    if dispatch_outbox:
        routes.outbox.dispatch(
            {"type": "Create", "object": {"type": "Audio"}}, context={"upload": upload}
        )


def federation_audio_track_to_metadata(payload):
    """
    Given a valid payload as returned by federation.serializers.TrackSerializer.validated_data,
    returns a correct metadata payload for use with get_track_from_import_metadata.
    """
    musicbrainz_recordingid = payload.get("musicbrainzId")
    musicbrainz_artistid = payload["artists"][0].get("musicbrainzId")
    musicbrainz_albumartistid = payload["album"]["artists"][0].get("musicbrainzId")
    musicbrainz_albumid = payload["album"].get("musicbrainzId")

    new_data = {
        "title": payload["name"],
        "album": payload["album"]["name"],
        "track_number": payload["position"],
        "artist": payload["artists"][0]["name"],
        "album_artist": payload["album"]["artists"][0]["name"],
        "date": payload["album"].get("released"),
        # musicbrainz
        "musicbrainz_recordingid": str(musicbrainz_recordingid)
        if musicbrainz_recordingid
        else None,
        "musicbrainz_artistid": str(musicbrainz_artistid)
        if musicbrainz_artistid
        else None,
        "musicbrainz_albumartistid": str(musicbrainz_albumartistid)
        if musicbrainz_albumartistid
        else None,
        "musicbrainz_albumid": str(musicbrainz_albumid)
        if musicbrainz_albumid
        else None,
        # federation
        "fid": payload["id"],
        "artist_fid": payload["artists"][0]["id"],
        "album_artist_fid": payload["album"]["artists"][0]["id"],
        "album_fid": payload["album"]["id"],
        "fdate": payload["published"],
        "album_fdate": payload["album"]["published"],
        "album_artist_fdate": payload["album"]["artists"][0]["published"],
        "artist_fdate": payload["artists"][0]["published"],
    }
    cover = payload["album"].get("cover")
    if cover:
        new_data["cover_data"] = {"mimetype": cover["mediaType"], "url": cover["href"]}
    return new_data


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


def get_best_candidate_or_create(model, query, defaults, sort_fields):
    """
    Like queryset.get_or_create() but does not crash if multiple objects
    are returned on the get() call
    """
    candidates = model.objects.filter(query)
    if candidates:

        return sort_candidates(candidates, sort_fields)[0], False

    return model.objects.create(**defaults), True


def sort_candidates(candidates, important_fields):
    """
    Given a list of objects and a list of fields,
    will return a sorted list of those objects by score.

    Score is higher for objects that have a non-empty attribute
    that is also present in important fields::

        artist1 = Artist(mbid=None, fid=None)
        artist2 = Artist(mbid="something", fid=None)

        # artist2 has a mbid, so is sorted first
        assert sort_candidates([artist1, artist2], ['mbid'])[0] == artist2

    Only supports string fields.
    """

    # map each fields to its score, giving a higher score to first fields
    fields_scores = {f: i + 1 for i, f in enumerate(sorted(important_fields))}
    candidates_with_scores = []
    for candidate in candidates:
        current_score = 0
        for field, score in fields_scores.items():
            v = getattr(candidate, field, "")
            if v:
                current_score += score

        candidates_with_scores.append((candidate, current_score))

    return [c for c, s in reversed(sorted(candidates_with_scores, key=lambda v: v[1]))]


@transaction.atomic
def get_track_from_import_metadata(data):
    track_uuid = getter(data, "funkwhale", "track", "uuid")

    if track_uuid:
        # easy case, we have a reference to a uuid of a track that
        # already exists in our database
        try:
            track = models.Track.objects.get(uuid=track_uuid)
        except models.Track.DoesNotExist:
            raise UploadImportError(code="track_uuid_not_found")

        if not track.album.cover:
            update_album_cover(
                track.album,
                source=data.get("upload_source"),
                cover_data=data.get("cover_data"),
            )
        return track

    from_activity_id = data.get("from_activity_id", None)
    track_mbid = data.get("musicbrainz_recordingid", None)
    album_mbid = data.get("musicbrainz_albumid", None)
    track_fid = getter(data, "fid")

    query = None

    if album_mbid and track_mbid:
        query = Q(mbid=track_mbid, album__mbid=album_mbid)

    if track_fid:
        query = query | Q(fid=track_fid) if query else Q(fid=track_fid)

    if query:
        # second easy case: we have a (track_mbid, album_mbid) pair or
        # a federation uuid we can check on
        try:
            return sort_candidates(models.Track.objects.filter(query), ["mbid", "fid"])[
                0
            ]
        except IndexError:
            pass

    # get / create artist and album artist
    artist_mbid = data.get("musicbrainz_artistid", None)
    artist_fid = data.get("artist_fid", None)
    artist_name = data["artist"]
    query = Q(name__iexact=artist_name)
    if artist_mbid:
        query |= Q(mbid=artist_mbid)
    if artist_fid:
        query |= Q(fid=artist_fid)
    defaults = {
        "name": artist_name,
        "mbid": artist_mbid,
        "fid": artist_fid,
        "from_activity_id": from_activity_id,
    }
    if data.get("artist_fdate"):
        defaults["creation_date"] = data.get("artist_fdate")

    artist = get_best_candidate_or_create(
        models.Artist, query, defaults=defaults, sort_fields=["mbid", "fid"]
    )[0]

    album_artist_name = data.get("album_artist", artist_name)
    if album_artist_name == artist_name:
        album_artist = artist
    else:
        query = Q(name__iexact=album_artist_name)
        album_artist_mbid = data.get("musicbrainz_albumartistid", None)
        album_artist_fid = data.get("album_artist_fid", None)
        if album_artist_mbid:
            query |= Q(mbid=album_artist_mbid)
        if album_artist_fid:
            query |= Q(fid=album_artist_fid)
        defaults = {
            "name": album_artist_name,
            "mbid": album_artist_mbid,
            "fid": album_artist_fid,
            "from_activity_id": from_activity_id,
        }
        if data.get("album_artist_fdate"):
            defaults["creation_date"] = data.get("album_artist_fdate")

        album_artist = get_best_candidate_or_create(
            models.Artist, query, defaults=defaults, sort_fields=["mbid", "fid"]
        )[0]

    # get / create album
    album_title = data["album"]
    album_fid = data.get("album_fid", None)
    query = Q(title__iexact=album_title, artist=album_artist)
    if album_mbid:
        query |= Q(mbid=album_mbid)
    if album_fid:
        query |= Q(fid=album_fid)
    defaults = {
        "title": album_title,
        "artist": album_artist,
        "mbid": album_mbid,
        "release_date": data.get("date"),
        "fid": album_fid,
        "from_activity_id": from_activity_id,
    }
    if data.get("album_fdate"):
        defaults["creation_date"] = data.get("album_fdate")

    album = get_best_candidate_or_create(
        models.Album, query, defaults=defaults, sort_fields=["mbid", "fid"]
    )[0]
    if not album.cover:
        update_album_cover(
            album, source=data.get("upload_source"), cover_data=data.get("cover_data")
        )

    # get / create track
    track_title = data["title"]
    track_number = data.get("track_number", 1)
    query = Q(title__iexact=track_title, artist=artist, album=album)
    if track_mbid:
        query |= Q(mbid=track_mbid)
    if track_fid:
        query |= Q(fid=track_fid)
    defaults = {
        "title": track_title,
        "album": album,
        "mbid": track_mbid,
        "artist": artist,
        "position": track_number,
        "fid": track_fid,
        "from_activity_id": from_activity_id,
    }
    if data.get("fdate"):
        defaults["creation_date"] = data.get("fdate")

    track = get_best_candidate_or_create(
        models.Track, query, defaults=defaults, sort_fields=["mbid", "fid"]
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
