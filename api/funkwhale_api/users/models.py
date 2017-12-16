# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

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
