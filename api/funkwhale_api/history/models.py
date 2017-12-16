from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from funkwhale_api.music.models import Track


class Listening(models.Model):
    end_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    track = models.ForeignKey(
        Track, related_name="listenings", on_delete=models.CASCADE)
    user = models.ForeignKey(
        'users.User',
        related_name="listenings",
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-end_date',)

    def save(self, **kwargs):
        if not self.user and not self.session_key:
            raise ValidationError('Cannot have both session_key and user empty for listening')

        super().save(**kwargs)
