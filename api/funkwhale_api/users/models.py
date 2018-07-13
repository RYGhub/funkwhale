# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import binascii
import datetime
import os
import random
import string
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from versatileimagefield.fields import VersatileImageField

from funkwhale_api.common import fields, preferences
from funkwhale_api.common import utils as common_utils
from funkwhale_api.common import validators as common_validators


def get_token():
    return binascii.b2a_hex(os.urandom(15)).decode("utf-8")


PERMISSIONS_CONFIGURATION = {
    "federation": {
        "label": "Manage library federation",
        "help_text": "Follow other instances, accept/deny library follow requests...",
    },
    "library": {
        "label": "Manage library",
        "help_text": "Manage library, delete files, tracks, artists, albums...",
    },
    "settings": {"label": "Manage instance-level settings", "help_text": ""},
    "upload": {"label": "Upload new content to the library", "help_text": ""},
}

PERMISSIONS = sorted(PERMISSIONS_CONFIGURATION.keys())


get_file_path = common_utils.ChunkedPath("users/avatars", preserve_file_name=False)


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    # updated on logout or password change, to invalidate JWT
    secret_key = models.UUIDField(default=uuid.uuid4, null=True)
    privacy_level = fields.get_privacy_field()

    # Unfortunately, Subsonic API assumes a MD5/password authentication
    # scheme, which is weak in terms of security, and not achievable
    # anyway since django use stronger schemes for storing passwords.
    # Users that want to use the subsonic API from external client
    # should set this token and use it as their password in such clients
    subsonic_api_token = models.CharField(blank=True, null=True, max_length=255)

    # permissions
    permission_federation = models.BooleanField(
        PERMISSIONS_CONFIGURATION["federation"]["label"],
        help_text=PERMISSIONS_CONFIGURATION["federation"]["help_text"],
        default=False,
    )
    permission_library = models.BooleanField(
        PERMISSIONS_CONFIGURATION["library"]["label"],
        help_text=PERMISSIONS_CONFIGURATION["library"]["help_text"],
        default=False,
    )
    permission_settings = models.BooleanField(
        PERMISSIONS_CONFIGURATION["settings"]["label"],
        help_text=PERMISSIONS_CONFIGURATION["settings"]["help_text"],
        default=False,
    )
    permission_upload = models.BooleanField(
        PERMISSIONS_CONFIGURATION["upload"]["label"],
        help_text=PERMISSIONS_CONFIGURATION["upload"]["help_text"],
        default=False,
    )

    last_activity = models.DateTimeField(default=None, null=True, blank=True)

    invitation = models.ForeignKey(
        "Invitation",
        related_name="users",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    avatar = VersatileImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        max_length=150,
        validators=[
            common_validators.ImageDimensionsValidator(min_width=50, min_height=50),
            common_validators.FileValidator(
                allowed_extensions=["png", "jpg", "jpeg", "gif"],
                max_size=1024 * 1024 * 2,
            ),
        ],
    )

    def __str__(self):
        return self.username

    def get_permissions(self, defaults=None):
        defaults = defaults or preferences.get("users__default_permissions")
        perms = {}
        for p in PERMISSIONS:
            v = (
                self.is_superuser
                or getattr(self, "permission_{}".format(p))
                or p in defaults
            )
            perms[p] = v
        return perms

    @property
    def all_permissions(self):
        return self.get_permissions()

    def has_permissions(self, *perms, **kwargs):
        operator = kwargs.pop("operator", "and")
        if operator not in ["and", "or"]:
            raise ValueError("Invalid operator {}".format(operator))
        permissions = self.get_permissions()
        checker = all if operator == "and" else any
        return checker([permissions[p] for p in perms])

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def update_secret_key(self):
        self.secret_key = uuid.uuid4()
        return self.secret_key

    def update_subsonic_api_token(self):
        self.subsonic_api_token = get_token()
        return self.subsonic_api_token

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.update_secret_key()
        if self.subsonic_api_token:
            self.update_subsonic_api_token()

    def get_activity_url(self):
        return settings.FUNKWHALE_URL + "/@{}".format(self.username)

    def record_activity(self):
        """
        Simply update the last_activity field if current value is too old
        than a threshold. This is useful to keep a track of inactive accounts.
        """
        current = self.last_activity
        delay = 60 * 15  # fifteen minutes
        now = timezone.now()

        if current is None or current < now - datetime.timedelta(seconds=delay):
            self.last_activity = now
            self.save(update_fields=["last_activity"])


def generate_code(length=10):
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase) for _ in range(length)
    )


class InvitationQuerySet(models.QuerySet):
    def open(self, include=True):
        now = timezone.now()
        qs = self.annotate(_users=models.Count("users"))
        query = models.Q(_users=0, expiration_date__gt=now)
        if include:
            return qs.filter(query)
        return qs.exclude(query)


class Invitation(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    owner = models.ForeignKey(
        User, related_name="invitations", on_delete=models.CASCADE
    )
    code = models.CharField(max_length=50, unique=True)

    objects = InvitationQuerySet.as_manager()

    def save(self, **kwargs):
        if not self.code:
            self.code = generate_code()
        if not self.expiration_date:
            self.expiration_date = self.creation_date + datetime.timedelta(
                days=settings.USERS_INVITATION_EXPIRATION_DAYS
            )

        return super().save(**kwargs)
