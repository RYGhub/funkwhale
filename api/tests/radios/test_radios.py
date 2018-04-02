import json
import random
import pytest

from django.urls import reverse
from django.core.exceptions import ValidationError


from funkwhale_api.radios import radios
from funkwhale_api.radios import models
from funkwhale_api.radios import serializers
from funkwhale_api.favorites.models import TrackFavorite


def test_can_pick_track_from_choices():
    choices = [1, 2, 3, 4, 5]

    radio = radios.SimpleRadio()

    first_pick = radio.pick(choices=choices)

    assert first_pick in choices

    previous_choices = [first_pick]
    for remaining_choice in choices:
        pick = radio.pick(choices=choices, previous_choices=previous_choices)
        assert pick in set(choices).difference(previous_choices)


def test_can_pick_by_weight():
    choices_with_weight = [
        # choice, weight
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    picks = {choice: 0 for choice, weight in choices_with_weight}

    for i in range(1000):
        radio = radios.SimpleRadio()
        pick = radio.weighted_pick(choices=choices_with_weight)
        picks[pick] = picks[pick] + 1

    assert picks[5] > picks[4]
    assert picks[4] > picks[3]
    assert picks[3] > picks[2]
    assert picks[2] > picks[1]


def test_can_get_choices_for_favorites_radio(factories):
    files = factories['music.TrackFile'].create_batch(10)
    tracks = [f.track for f in files]
    user = factories['users.User']()
    for i in range(5):
        TrackFavorite.add(track=random.choice(tracks), user=user)

    radio = radios.FavoritesRadio()
    choices = radio.get_choices(user=user)

    assert choices.count() == user.track_favorites.all().count()

    for favorite in user.track_favorites.all():
        assert favorite.track in choices

    for i in range(5):
        pick = radio.pick(user=user)
        assert pick in choices


def test_can_get_choices_for_custom_radio(factories):
    artist = factories['music.Artist']()
    files = factories['music.TrackFile'].create_batch(
        5, track__artist=artist)
    tracks = [f.track for f in files]
    wrong_files = factories['music.TrackFile'].create_batch(5)
    wrong_tracks = [f.track for f in wrong_files]

    session = factories['radios.CustomRadioSession'](
        custom_radio__config=[{'type': 'artist', 'ids': [artist.pk]}]
    )
    choices = session.radio.get_choices()

    expected = [t.pk for t in tracks]
    assert list(choices.values_list('id', flat=True)) == expected


def test_cannot_start_custom_radio_if_not_owner_or_not_public(factories):
    user = factories['users.User']()
    artist = factories['music.Artist']()
    radio = factories['radios.Radio'](
        config=[{'type': 'artist', 'ids': [artist.pk]}]
    )
    serializer = serializers.RadioSessionSerializer(
        data={
            'radio_type': 'custom', 'custom_radio': radio.pk, 'user': user.pk}
    )
    message = "You don't have access to this radio"
    assert not serializer.is_valid()
    assert message in serializer.errors['non_field_errors']


def test_can_start_custom_radio_from_api(logged_in_client, factories):
    artist = factories['music.Artist']()
    radio = factories['radios.Radio'](
        config=[{'type': 'artist', 'ids': [artist.pk]}],
        user=logged_in_client.user
    )
    url = reverse('api:v1:radios:sessions-list')
    response = logged_in_client.post(
        url, {'radio_type': 'custom', 'custom_radio': radio.pk})
    assert response.status_code == 201
    session = radio.sessions.latest('id')
    assert session.radio_type == 'custom'
    assert session.user == logged_in_client.user


def test_can_use_radio_session_to_filter_choices(factories):
    files = factories['music.TrackFile'].create_batch(30)
    tracks = [f.track for f in files]
    user = factories['users.User']()
    radio = radios.RandomRadio()
    session = radio.start_session(user)

    for i in range(30):
        p = radio.pick()

    # ensure 30 differents tracks have been suggested
    tracks_id = [
        session_track.track.pk
        for session_track in session.session_tracks.all()]
    assert len(set(tracks_id)) == 30


def test_can_restore_radio_from_previous_session(factories):
    user = factories['users.User']()
    radio = radios.RandomRadio()
    session = radio.start_session(user)

    restarted_radio = radios.RandomRadio(session)
    assert radio.session == restarted_radio.session


def test_can_start_radio_for_logged_in_user(logged_in_client):
    url = reverse('api:v1:radios:sessions-list')
    response = logged_in_client.post(url, {'radio_type': 'random'})
    session = models.RadioSession.objects.latest('id')
    assert session.radio_type == 'random'
    assert session.user == logged_in_client.user


def test_can_start_radio_for_anonymous_user(api_client, db, settings):
    settings.API_AUTHENTICATION_REQUIRED = False
    url = reverse('api:v1:radios:sessions-list')
    response = api_client.post(url, {'radio_type': 'random'})

    assert response.status_code == 201

    session = models.RadioSession.objects.latest('id')

    assert session.radio_type == 'random'
    assert session.user is None
    assert session.session_key == api_client.session.session_key


def test_can_get_track_for_session_from_api(factories, logged_in_client):
    files = factories['music.TrackFile'].create_batch(1)
    tracks = [f.track for f in files]
    url = reverse('api:v1:radios:sessions-list')
    response = logged_in_client.post(url, {'radio_type': 'random'})
    session = models.RadioSession.objects.latest('id')

    url = reverse('api:v1:radios:tracks-list')
    response = logged_in_client.post(url, {'session': session.pk})
    data = json.loads(response.content.decode('utf-8'))

    assert data['track']['id'] == tracks[0].id
    assert data['position'] == 1

    next_track = factories['music.TrackFile']().track
    response = logged_in_client.post(url, {'session': session.pk})
    data = json.loads(response.content.decode('utf-8'))

    assert data['track']['id'] == next_track.id
    assert data['position'] == 2


def test_related_object_radio_validate_related_object(factories):
    user = factories['users.User']()
    # cannot start without related object
    radio = radios.ArtistRadio()
    with pytest.raises(ValidationError):
        radio.start_session(user)

    # cannot start with bad related object type
    radio = radios.ArtistRadio()
    with pytest.raises(ValidationError):
        radio.start_session(user, related_object=user)


def test_can_start_artist_radio(factories):
    user = factories['users.User']()
    artist = factories['music.Artist']()
    wrong_files = factories['music.TrackFile'].create_batch(5)
    wrong_tracks = [f.track for f in wrong_files]
    good_files = factories['music.TrackFile'].create_batch(
        5, track__artist=artist)
    good_tracks = [f.track for f in good_files]

    radio = radios.ArtistRadio()
    session = radio.start_session(user, related_object=artist)
    assert session.radio_type == 'artist'
    for i in range(5):
        assert radio.pick() in good_tracks


def test_can_start_tag_radio(factories):
    user = factories['users.User']()
    tag = factories['taggit.Tag']()
    wrong_files = factories['music.TrackFile'].create_batch(5)
    wrong_tracks = [f.track for f in wrong_files]
    good_files = factories['music.TrackFile'].create_batch(
        5, track__tags=[tag])
    good_tracks = [f.track for f in good_files]

    radio = radios.TagRadio()
    session = radio.start_session(user, related_object=tag)
    assert session.radio_type =='tag'
    for i in range(5):
        assert radio.pick() in good_tracks


def test_can_start_artist_radio_from_api(api_client, settings, factories):
    settings.API_AUTHENTICATION_REQUIRED = False
    artist = factories['music.Artist']()
    url = reverse('api:v1:radios:sessions-list')

    response = api_client.post(
        url, {'radio_type': 'artist', 'related_object_id': artist.id})

    assert response.status_code == 201

    session = models.RadioSession.objects.latest('id')

    assert session.radio_type, 'artist'
    assert session.related_object, artist


def test_can_start_less_listened_radio(factories):
    user = factories['users.User']()
    wrong_files = factories['music.TrackFile'].create_batch(5)
    for f in wrong_files:
        factories['history.Listening'](track=f.track, user=user)
    good_files = factories['music.TrackFile'].create_batch(5)
    good_tracks = [f.track for f in good_files]
    radio = radios.LessListenedRadio()
    session = radio.start_session(user)
    assert session.related_object == user
    for i in range(5):
        assert radio.pick() in good_tracks
