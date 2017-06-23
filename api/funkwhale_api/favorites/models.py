from django.db import models
from django.utils import timezone

from funkwhale_api.music.models import Track

class TrackFavorite(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey('users.User', related_name='track_favorites')
    track = models.ForeignKey(Track, related_name='track_favorites')

    class Meta:
        unique_together = ('track', 'user')
        ordering = ('-creation_date',)

    @classmethod
    def add(cls, track, user):
        favorite, created = cls.objects.get_or_create(user=user, track=track)
        return favorite
