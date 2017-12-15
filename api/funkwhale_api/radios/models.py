from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from funkwhale_api.music.models import Track

class RadioSession(models.Model):
    user = models.ForeignKey(
        'users.User',
        related_name='radio_sessions',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    radio_type = models.CharField(max_length=50)
    creation_date = models.DateTimeField(default=timezone.now)
    related_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = GenericForeignKey('related_object_content_type', 'related_object_id')

    def save(self, **kwargs):
        if not self.user and not self.session_key:
            raise ValidationError('Cannot have both session_key and user empty for radio session')
        self.radio.clean(self)
        super().save(**kwargs)

    @property
    def next_position(self):
        next_position = 1

        last_session_track = self.session_tracks.all().order_by('-position').first()
        if last_session_track:
            next_position = last_session_track.position + 1

        return next_position

    def add(self, track):
        new_session_track = RadioSessionTrack.objects.create(track=track, session=self, position=self.next_position)

        return new_session_track

    @property
    def radio(self):
        from .registries import registry
        from . import radios
        return registry[self.radio_type](session=self)

class RadioSessionTrack(models.Model):
    session = models.ForeignKey(
        RadioSession, related_name='session_tracks', on_delete=models.CASCADE)
    position = models.IntegerField(default=1)
    track = models.ForeignKey(
        Track, related_name='radio_session_tracks', on_delete=models.CASCADE)

    class Meta:
        ordering = ('session', 'position')
        unique_together = ('session', 'position')
