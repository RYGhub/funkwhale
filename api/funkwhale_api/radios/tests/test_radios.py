import random
import json
from test_plus.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError


from funkwhale_api.radios import radios
from funkwhale_api.radios import models
from funkwhale_api.favorites.models import TrackFavorite
from funkwhale_api.users.models import User
from funkwhale_api.music.models import Artist
from funkwhale_api.music.tests import factories
from funkwhale_api.history.tests.factories import ListeningFactory


class TestRadios(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test')

    def test_can_pick_track_from_choices(self):
        choices = [1, 2, 3, 4, 5]

        radio = radios.SimpleRadio()

        first_pick = radio.pick(choices=choices)

        self.assertIn(first_pick, choices)

        previous_choices = [first_pick]
        for remaining_choice in choices:
            pick = radio.pick(choices=choices, previous_choices=previous_choices)
            self.assertIn(pick, set(choices).difference(previous_choices))

    def test_can_pick_by_weight(self):
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

        self.assertTrue(picks[5] > picks[4])
        self.assertTrue(picks[4] > picks[3])
        self.assertTrue(picks[3] > picks[2])
        self.assertTrue(picks[2] > picks[1])

    def test_can_get_choices_for_favorites_radio(self):
        tracks = factories.TrackFactory.create_batch(size=100)

        for i in range(20):
            TrackFavorite.add(track=random.choice(tracks), user=self.user)

        radio = radios.FavoritesRadio()
        choices = radio.get_choices(user=self.user)

        self.assertEqual(choices.count(), self.user.track_favorites.all().count())

        for favorite in self.user.track_favorites.all():
            self.assertIn(favorite.track, choices)

        for i in range(20):
            pick = radio.pick(user=self.user)
            self.assertIn(pick, choices)

    def test_can_use_radio_session_to_filter_choices(self):
        tracks = factories.TrackFactory.create_batch(size=30)
        radio = radios.RandomRadio()
        session = radio.start_session(self.user)

        for i in range(30):
            p = radio.pick()

        # ensure 30 differents tracks have been suggested
        tracks_id = [session_track.track.pk for session_track in session.session_tracks.all()]
        self.assertEqual(len(set(tracks_id)), 30)

    def test_can_restore_radio_from_previous_session(self):
        tracks = factories.TrackFactory.create_batch(size=30)

        radio = radios.RandomRadio()
        session = radio.start_session(self.user)

        restarted_radio = radios.RandomRadio(session)
        self.assertEqual(radio.session, restarted_radio.session)

    def test_can_get_start_radio_from_api(self):
        url = reverse('api:v1:radios:sessions-list')
        response = self.client.post(url, {'radio_type': 'random'})
        session = models.RadioSession.objects.latest('id')
        self.assertEqual(session.radio_type, 'random')
        self.assertEqual(session.user, None)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(url, {'radio_type': 'random'})
        session = models.RadioSession.objects.latest('id')
        self.assertEqual(session.radio_type, 'random')
        self.assertEqual(session.user, self.user)

    def test_can_start_radio_for_anonymous_user(self):
        url = reverse('api:v1:radios:sessions-list')
        response = self.client.post(url, {'radio_type': 'random'})
        session = models.RadioSession.objects.latest('id')

        self.assertIsNone(session.user)
        self.assertIsNotNone(session.session_key)

    def test_can_get_track_for_session_from_api(self):
        tracks = factories.TrackFactory.create_batch(size=1)

        self.client.login(username=self.user.username, password='test')
        url = reverse('api:v1:radios:sessions-list')
        response = self.client.post(url, {'radio_type': 'random'})
        session = models.RadioSession.objects.latest('id')

        url = reverse('api:v1:radios:tracks-list')
        response = self.client.post(url, {'session': session.pk})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(data['track']['id'], tracks[0].id)
        self.assertEqual(data['position'], 1)

        next_track = factories.TrackFactory()
        response = self.client.post(url, {'session': session.pk})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(data['track']['id'], next_track.id)
        self.assertEqual(data['position'], 2)

    def test_related_object_radio_validate_related_object(self):
        # cannot start without related object
        radio = radios.ArtistRadio()
        with self.assertRaises(ValidationError):
            radio.start_session(self.user)

        # cannot start with bad related object type
        radio = radios.ArtistRadio()
        with self.assertRaises(ValidationError):
            radio.start_session(self.user, related_object=self.user)

    def test_can_start_artist_radio(self):
        artist = factories.ArtistFactory()
        wrong_tracks = factories.TrackFactory.create_batch(size=30)
        good_tracks = factories.TrackFactory.create_batch(
            artist=artist, size=5)

        radio = radios.ArtistRadio()
        session = radio.start_session(self.user, related_object=artist)
        self.assertEqual(session.radio_type, 'artist')
        for i in range(5):
            self.assertIn(radio.pick(), good_tracks)

    def test_can_start_tag_radio(self):
        tag = factories.TagFactory()
        wrong_tracks = factories.TrackFactory.create_batch(size=30)
        good_tracks = factories.TrackFactory.create_batch(size=5)
        for track in good_tracks:
            track.tags.add(tag)

        radio = radios.TagRadio()
        session = radio.start_session(self.user, related_object=tag)
        self.assertEqual(session.radio_type, 'tag')
        for i in range(5):
            self.assertIn(radio.pick(), good_tracks)

    def test_can_start_artist_radio_from_api(self):
        artist = factories.ArtistFactory()
        url = reverse('api:v1:radios:sessions-list')

        response = self.client.post(url, {'radio_type': 'artist', 'related_object_id': artist.id})
        session = models.RadioSession.objects.latest('id')
        self.assertEqual(session.radio_type, 'artist')
        self.assertEqual(session.related_object, artist)

    def test_can_start_less_listened_radio(self):
        history = ListeningFactory.create_batch(size=5, user=self.user)
        wrong_tracks = [h.track for h in history]

        good_tracks = factories.TrackFactory.create_batch(size=30)

        radio = radios.LessListenedRadio()
        session = radio.start_session(self.user)
        self.assertEqual(session.related_object, self.user)
        for i in range(5):
            self.assertIn(radio.pick(), good_tracks)
