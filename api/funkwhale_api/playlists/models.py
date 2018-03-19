from django import forms
from django.db import models
from django.db import transaction
from django.utils import timezone

from funkwhale_api.common import fields


class Playlist(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        'users.User', related_name="playlists", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    privacy_level = fields.get_privacy_field()

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
            raise forms.ValidationError('Index is not continuous')

        if index < 0:
            raise forms.ValidationError('Index must be zero or positive')

        if move:
            # we remove the index temporarily, to avoid integrity errors
            plt.index = None
            plt.save(update_fields=['index'])

        if move:
            if index > old_index:
                # new index is higher than current, we decrement previous tracks
                to_update = existing.filter(
                    index__gt=old_index, index__lte=index)
                to_update.update(index=models.F('index') - 1)
            if index < old_index:
                # new index is lower than current, we increment next tracks
                to_update = existing.filter(
                    index__lt=old_index, index__gte=index)
                to_update.update(index=models.F('index') + 1)
        else:
            to_update = existing.filter(index__gte=index)
            to_update.update(index=models.F('index') + 1)

        plt.index = index
        plt.save(update_fields=['index'])
        return index


class PlaylistTrack(models.Model):
    track = models.ForeignKey(
        'music.Track',
        related_name='playlist_tracks',
        on_delete=models.CASCADE)
    index = models.PositiveIntegerField(null=True)
    playlist = models.ForeignKey(
        Playlist, related_name='playlist_tracks', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-playlist', 'index')
        unique_together = ('playlist', 'index')
