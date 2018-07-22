from django.db import models, transaction
from django.utils import timezone
from rest_framework import exceptions

from funkwhale_api.common import fields, preferences
from funkwhale_api.music import models as music_models


class PlaylistQuerySet(models.QuerySet):
    def with_tracks_count(self):
        return self.annotate(_tracks_count=models.Count("playlist_tracks"))

    def with_duration(self):
        return self.annotate(
            duration=models.Sum("playlist_tracks__track__files__duration")
        )

    def with_covers(self):
        album_prefetch = models.Prefetch(
            "album", queryset=music_models.Album.objects.only("cover")
        )
        track_prefetch = models.Prefetch(
            "track",
            queryset=music_models.Track.objects.prefetch_related(album_prefetch).only(
                "id", "album_id"
            ),
        )

        plt_prefetch = models.Prefetch(
            "playlist_tracks",
            queryset=PlaylistTrack.objects.all()
            .exclude(track__album__cover=None)
            .exclude(track__album__cover="")
            .order_by("index")
            .only("id", "playlist_id", "track_id")
            .prefetch_related(track_prefetch),
            to_attr="plts_for_cover",
        )
        return self.prefetch_related(plt_prefetch)


class Playlist(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        "users.User", related_name="playlists", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    privacy_level = fields.get_privacy_field()

    objects = PlaylistQuerySet.as_manager()

    def __str__(self):
        return self.name

    @transaction.atomic
    def insert(self, plt, index=None):
        """
        Given a PlaylistTrack, insert it at the correct index in the playlist,
        and update other tracks index if necessary.
        """
        old_index = plt.index
        move = old_index is not None
        if index is not None and index == old_index:
            # moving at same position, just skip
            return index

        existing = self.playlist_tracks.select_for_update()
        if move:
            existing = existing.exclude(pk=plt.pk)
        total = existing.filter(index__isnull=False).count()

        if index is None:
            # we simply increment the last track index by 1
            index = total

        if index > total:
            raise exceptions.ValidationError("Index is not continuous")

        if index < 0:
            raise exceptions.ValidationError("Index must be zero or positive")

        if move:
            # we remove the index temporarily, to avoid integrity errors
            plt.index = None
            plt.save(update_fields=["index"])
            if index > old_index:
                # new index is higher than current, we decrement previous tracks
                to_update = existing.filter(index__gt=old_index, index__lte=index)
                to_update.update(index=models.F("index") - 1)
            if index < old_index:
                # new index is lower than current, we increment next tracks
                to_update = existing.filter(index__lt=old_index, index__gte=index)
                to_update.update(index=models.F("index") + 1)
        else:
            to_update = existing.filter(index__gte=index)
            to_update.update(index=models.F("index") + 1)

        plt.index = index
        plt.save(update_fields=["index"])
        self.save(update_fields=["modification_date"])
        return index

    @transaction.atomic
    def remove(self, index):
        existing = self.playlist_tracks.select_for_update()
        self.save(update_fields=["modification_date"])
        to_update = existing.filter(index__gt=index)
        return to_update.update(index=models.F("index") - 1)

    @transaction.atomic
    def insert_many(self, tracks):
        existing = self.playlist_tracks.select_for_update()
        now = timezone.now()
        total = existing.filter(index__isnull=False).count()
        max_tracks = preferences.get("playlists__max_tracks")
        if existing.count() + len(tracks) > max_tracks:
            raise exceptions.ValidationError(
                "Playlist would reach the maximum of {} tracks".format(max_tracks)
            )
        self.save(update_fields=["modification_date"])
        start = total
        plts = [
            PlaylistTrack(
                creation_date=now, playlist=self, track=track, index=start + i
            )
            for i, track in enumerate(tracks)
        ]
        return PlaylistTrack.objects.bulk_create(plts)


class PlaylistTrackQuerySet(models.QuerySet):
    def for_nested_serialization(self):
        return (
            self.select_related()
            .select_related("track__album__artist")
            .prefetch_related(
                "track__tags", "track__files", "track__artist__albums__tracks__tags"
            )
        )


class PlaylistTrack(models.Model):
    track = models.ForeignKey(
        "music.Track", related_name="playlist_tracks", on_delete=models.CASCADE
    )
    index = models.PositiveIntegerField(null=True, blank=True)
    playlist = models.ForeignKey(
        Playlist, related_name="playlist_tracks", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(default=timezone.now)

    objects = PlaylistTrackQuerySet.as_manager()

    class Meta:
        ordering = ("-playlist", "index")
        unique_together = ("playlist", "index")

    def delete(self, *args, **kwargs):
        playlist = self.playlist
        index = self.index
        update_indexes = kwargs.pop("update_indexes", False)
        r = super().delete(*args, **kwargs)
        if index is not None and update_indexes:
            playlist.remove(index)
        return r
