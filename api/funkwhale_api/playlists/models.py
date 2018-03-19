from django.db import models
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

    def add_track(self, track, previous=None):
        plt = PlaylistTrack(previous=previous, track=track, playlist=self)
        plt.save()

        return plt


class PlaylistTrack(MPTTModel):
    track = models.ForeignKey(
        'music.Track',
        related_name='playlist_tracks',
        on_delete=models.CASCADE)
    index = models.PositiveIntegerField(null=True)
    playlist = models.ForeignKey(
        Playlist, related_name='playlist_tracks', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-playlist', 'index')
        unique_together = ('playlist', 'index')
