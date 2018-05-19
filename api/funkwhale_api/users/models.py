# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import binascii
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.urls import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from funkwhale_api.common import fields


def get_token():
    return binascii.b2a_hex(os.urandom(15)).decode('utf-8')


PERMISSIONS = [
    'federation',
    'library',
    'settings',
]


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
    subsonic_api_token = models.CharField(
        blank=True, null=True, max_length=255)

    # permissions
    permission_federation = models.BooleanField(
        'Manage library federation',
        help_text='Follow other instances, accept/deny library follow requests...',
        default=False)
    permission_library = models.BooleanField(
        'Manage library',
        help_text='Import new content, manage existing content',
        default=False)
    permission_settings = models.BooleanField(
        'Manage instance-level settings',
        default=False)

    def __str__(self):
        return self.username

    def get_permissions(self):
        perms = {}
        for p in PERMISSIONS:
            v = self.is_superuser or getattr(self, 'permission_{}'.format(p))
            perms[p] = v
        return perms

    def has_permissions(self, *perms):
        permissions = self.get_permissions()
        return all([permissions[p] for p in perms])

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

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
        return settings.FUNKWHALE_URL + '/@{}'.format(self.username)
