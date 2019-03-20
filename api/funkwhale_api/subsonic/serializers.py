import collections

from django.db.models import Count, functions
from rest_framework import serializers

from funkwhale_api.history import models as history_models
from funkwhale_api.music import models as music_models


def get_artist_data(artist_values):
    return {
        "id": artist_values["id"],
        "name": artist_values["name"],
        "albumCount": artist_values["_albums_count"],
    }


class GetArtistsSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        payload = {"ignoredArticles": "", "index": []}
        queryset = queryset.with_albums_count()
        queryset = queryset.order_by(functions.Lower("name"))
        values = queryset.values("id", "_albums_count", "name")

        first_letter_mapping = collections.defaultdict(list)
        for artist in values:
            if artist["name"]:
                first_letter_mapping[artist["name"][0].upper()].append(artist)

        for letter, artists in sorted(first_letter_mapping.items()):
            letter_data = {
                "name": letter,
                "artist": [get_artist_data(v) for v in artists],
            }
            payload["index"].append(letter_data)
        return payload


class GetArtistSerializer(serializers.Serializer):
    def to_representation(self, artist):
        albums = artist.albums.prefetch_related("tracks__uploads")
        payload = {
            "id": artist.pk,
            "name": artist.name,
            "albumCount": len(albums),
            "album": [],
        }
        for album in albums:
            album_data = {
                "id": album.id,
                "artistId": artist.id,
                "name": album.title,
                "artist": artist.name,
                "created": album.creation_date,
                "songCount": len(album.tracks.all()),
            }
            if album.cover:
                album_data["coverArt"] = "al-{}".format(album.id)
            if album.release_date:
                album_data["year"] = album.release_date.year
            payload["album"].append(album_data)
        return payload


def get_track_data(album, track, upload):
    data = {
        "id": track.pk,
        "isDir": "false",
        "title": track.title,
        "album": album.title,
        "artist": album.artist.name,
        "track": track.position or 1,
        "discNumber": track.disc_number or 1,
        "contentType": upload.mimetype,
        "suffix": upload.extension or "",
        "duration": upload.duration or 0,
        "created": track.creation_date,
        "albumId": album.pk,
        "artistId": album.artist.pk,
        "type": "music",
    }
    if track.album.cover:
        data["coverArt"] = "al-{}".format(track.album.id)
    if upload.bitrate:
        data["bitrate"] = int(upload.bitrate / 1000)
    if upload.size:
        data["size"] = upload.size
    if album.release_date:
        data["year"] = album.release_date.year
    return data


def get_album2_data(album):
    payload = {
        "id": album.id,
        "artistId": album.artist.id,
        "name": album.title,
        "artist": album.artist.name,
        "created": album.creation_date,
    }
    if album.cover:
        payload["coverArt"] = "al-{}".format(album.id)

    try:
        payload["songCount"] = album._tracks_count
    except AttributeError:
        payload["songCount"] = len(album.tracks.prefetch_related("uploads"))
    return payload


def get_song_list_data(tracks):
    songs = []
    for track in tracks:
        try:
            uploads = [upload for upload in track.uploads.all()][0]
        except IndexError:
            continue
        track_data = get_track_data(track.album, track, uploads)
        songs.append(track_data)
    return songs


class GetAlbumSerializer(serializers.Serializer):
    def to_representation(self, album):
        tracks = album.tracks.prefetch_related("uploads").select_related("album")
        payload = get_album2_data(album)
        if album.release_date:
            payload["year"] = album.release_date.year

        payload["song"] = get_song_list_data(tracks)
        return payload


class GetSongSerializer(serializers.Serializer):
    def to_representation(self, track):
        uploads = track.uploads.all()
        if not len(uploads):
            return {}
        return get_track_data(track.album, track, uploads[0])


def get_starred_tracks_data(favorites):
    by_track_id = {f.track_id: f for f in favorites}
    tracks = (
        music_models.Track.objects.filter(pk__in=by_track_id.keys())
        .select_related("album__artist")
        .prefetch_related("uploads")
    )
    tracks = tracks.order_by("-creation_date")
    data = []
    for t in tracks:
        try:
            uploads = [upload for upload in t.uploads.all()][0]
        except IndexError:
            continue
        td = get_track_data(t.album, t, uploads)
        td["starred"] = by_track_id[t.pk].creation_date
        data.append(td)
    return data


def get_album_list2_data(albums):
    return [get_album2_data(a) for a in albums]


def get_playlist_data(playlist):
    return {
        "id": playlist.pk,
        "name": playlist.name,
        "owner": playlist.user.username,
        "public": "false",
        "songCount": playlist._tracks_count,
        "duration": 0,
        "created": playlist.creation_date,
    }


def get_playlist_detail_data(playlist):
    data = get_playlist_data(playlist)
    qs = (
        playlist.playlist_tracks.select_related("track__album__artist")
        .prefetch_related("track__uploads")
        .order_by("index")
    )
    data["entry"] = []
    for plt in qs:
        try:
            uploads = [upload for upload in plt.track.uploads.all()][0]
        except IndexError:
            continue
        td = get_track_data(plt.track.album, plt.track, uploads)
        data["entry"].append(td)
    return data


def get_music_directory_data(artist):
    tracks = artist.tracks.select_related("album").prefetch_related("uploads")
    data = {"id": artist.pk, "parent": 1, "name": artist.name, "child": []}
    for track in tracks:
        try:
            upload = [upload for upload in track.uploads.all()][0]
        except IndexError:
            continue
        album = track.album
        td = {
            "id": track.pk,
            "isDir": "false",
            "title": track.title,
            "album": album.title,
            "artist": artist.name,
            "track": track.position or 1,
            "year": track.album.release_date.year if track.album.release_date else 0,
            "contentType": upload.mimetype,
            "suffix": upload.extension or "",
            "duration": upload.duration or 0,
            "created": track.creation_date,
            "albumId": album.pk,
            "artistId": artist.pk,
            "parent": artist.id,
            "type": "music",
        }
        if upload.bitrate:
            td["bitrate"] = int(upload.bitrate / 1000)
        if upload.size:
            td["size"] = upload.size
        data["child"].append(td)
    return data


def get_folders(user):
    return []


def get_user_detail_data(user):
    return {
        "username": user.username,
        "email": user.email,
        "scrobblingEnabled": "true",
        "adminRole": "false",
        "settingsRole": "false",
        "commentRole": "false",
        "podcastRole": "false",
        "coverArtRole": "false",
        "shareRole": "false",
        "uploadRole": "true",
        "downloadRole": "true",
        "playlistRole": "true",
        "streamRole": "true",
        "jukeboxRole": "true",
        "folder": [f["id"] for f in get_folders(user)],
    }


class ScrobbleSerializer(serializers.Serializer):
    submission = serializers.BooleanField(default=True, required=False)
    id = serializers.PrimaryKeyRelatedField(
        queryset=music_models.Track.objects.annotate(
            uploads_count=Count("uploads")
        ).filter(uploads_count__gt=0)
    )

    def create(self, data):
        return history_models.Listening.objects.create(
            user=self.context["user"], track=data["id"]
        )
