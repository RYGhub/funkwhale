from django.db import transaction

from funkwhale_api.music import metadata, models


@transaction.atomic
def import_track_data_from_path(path):
    data = metadata.Metadata(path)
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
