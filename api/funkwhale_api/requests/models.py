from django.db import models
from django.utils import timezone

NATURE_CHOICES = [("artist", "artist"), ("album", "album"), ("track", "track")]

STATUS_CHOICES = [
    ("pending", "pending"),
    ("accepted", "accepted"),
    ("imported", "imported"),
    ("closed", "closed"),
]


class ImportRequest(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    imported_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User", related_name="import_requests", on_delete=models.CASCADE
    )
    artist_name = models.CharField(max_length=250)
    albums = models.CharField(max_length=3000, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default="pending")
    comment = models.TextField(null=True, blank=True, max_length=3000)
