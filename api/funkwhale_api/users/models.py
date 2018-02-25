# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    # updated on logout or password change, to invalidate JWT
    secret_key = models.UUIDField(default=uuid.uuid4, null=True)
    # permissions that are used for API access and that worth serializing
    relevant_permissions = {
        # internal_codename : {external_codename}
        'music.add_importbatch': {
            'external_codename': 'import.launch',
        },
        'dynamic_preferences.change_globalpreferencemodel': {
            'external_codename': 'settings.change',
        },
    }

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def update_secret_key(self):
        self.secret_key = uuid.uuid4()
        return self.secret_key

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.update_secret_key()

    def get_activity_url(self):
        return settings.FUNKWHALE_URL + '/@{}'.format(self.username)
