from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeOneToOneField


class Playlist(models.Model):
    name = models.CharField(max_length=50)
    is_public = models.BooleanField(default=False)
    user = models.ForeignKey(
        'users.User', related_name="playlists", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def add_track(self, track, previous=None):
        plt = PlaylistTrack(previous=previous, track=track, playlist=self)
        plt.save()

        return plt


class PlaylistTrack(MPTTModel):
    track = models.ForeignKey(
        'music.Track',
        related_name='playlist_tracks',
        on_delete=models.CASCADE)
    previous = TreeOneToOneField(
        'self',
        blank=True,
        null=True,
        related_name='next',
        on_delete=models.CASCADE)
    playlist = models.ForeignKey(
        Playlist, related_name='playlist_tracks', on_delete=models.CASCADE)

    class MPTTMeta:
        level_attr = 'position'
        parent_attr = 'previous'

    class Meta:
        ordering = ('-playlist', 'position')
