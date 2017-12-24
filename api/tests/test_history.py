import random
import json
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from funkwhale_api.history import models


def test_can_create_listening(factories):
    track = factories['music.Track']()
    user = factories['users.User']()
    now = timezone.now()
    l = models.Listening.objects.create(user=user, track=track)


def test_anonymous_user_can_create_listening_via_api(client, factories, settings):
    settings.API_AUTHENTICATION_REQUIRED = False
    track = factories['music.Track']()
    url = reverse('api:v1:history:listenings-list')
    response = client.post(url, {
        'track': track.pk,
    })

    listening = models.Listening.objects.latest('id')

    assert listening.track == track
    assert listening.session_key == client.session.session_key


def test_logged_in_user_can_create_listening_via_api(logged_in_client, factories):
    track = factories['music.Track']()

    url = reverse('api:v1:history:listenings-list')
    response = logged_in_client.post(url, {
        'track': track.pk,
    })

    listening = models.Listening.objects.latest('id')

    assert listening.track == track
    assert listening.user == logged_in_client.user
