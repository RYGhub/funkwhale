from django.db.models import Sum

from funkwhale_api.favorites.models import TrackFavorite
from funkwhale_api.history.models import Listening
from funkwhale_api.music import models
from funkwhale_api.users.models import User


def get():
    return {
        "users": get_users(),
        "tracks": get_tracks(),
        "albums": get_albums(),
        "artists": get_artists(),
        "track_favorites": get_track_favorites(),
        "listenings": get_listenings(),
        "music_duration": get_music_duration(),
    }


def get_users():
    return User.objects.count()


def get_listenings():
    return Listening.objects.count()


def get_track_favorites():
    return TrackFavorite.objects.count()


def get_tracks():
    return models.Track.objects.count()


def get_albums():
    return models.Album.objects.count()


def get_artists():
    return models.Artist.objects.count()


def get_music_duration():
    seconds = models.TrackFile.objects.aggregate(d=Sum("duration"))["d"]
    if seconds:
        return seconds / 3600
    return 0
