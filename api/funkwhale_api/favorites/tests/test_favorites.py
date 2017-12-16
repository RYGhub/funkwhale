import json
from test_plus.test import TestCase
from django.urls import reverse

from funkwhale_api.music.models import Track, Artist
from funkwhale_api.favorites.models import TrackFavorite
from funkwhale_api.users.models import User

class TestFavorites(TestCase):

    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='test')
        self.track = Track.objects.create(title='test', artist=self.artist)
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test')

    def test_user_can_add_favorite(self):
        TrackFavorite.add(self.track, self.user)

        favorite = TrackFavorite.objects.latest('id')
        self.assertEqual(favorite.track, self.track)
        self.assertEqual(favorite.user, self.user)

    def test_user_can_get_his_favorites(self):
        favorite = TrackFavorite.add(self.track, self.user)

        url = reverse('api:v1:favorites:tracks-list')
        self.client.login(username=self.user.username, password='test')

        response = self.client.get(url)

        expected = [
            {
                'track': self.track.pk,
                'id': favorite.id,
                'creation_date': favorite.creation_date.isoformat().replace('+00:00', 'Z'),
            }
        ]
        parsed_json = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, parsed_json['results'])

    def test_user_can_add_favorite_via_api(self):
        url = reverse('api:v1:favorites:tracks-list')
        self.client.login(username=self.user.username, password='test')
        response = self.client.post(url, {'track': self.track.pk})

        favorite = TrackFavorite.objects.latest('id')
        expected = {
            'track': self.track.pk,
            'id': favorite.id,
            'creation_date': favorite.creation_date.isoformat().replace('+00:00', 'Z'),
        }
        parsed_json = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, parsed_json)
        self.assertEqual(favorite.track, self.track)
        self.assertEqual(favorite.user, self.user)

    def test_user_can_remove_favorite_via_api(self):
        favorite = TrackFavorite.add(self.track, self.user)

        url = reverse('api:v1:favorites:tracks-detail', kwargs={'pk': favorite.pk})
        self.client.login(username=self.user.username, password='test')
        response = self.client.delete(url, {'track': self.track.pk})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(TrackFavorite.objects.count(), 0)

    def test_user_can_remove_favorite_via_api_using_track_id(self):
        favorite = TrackFavorite.add(self.track, self.user)

        url = reverse('api:v1:favorites:tracks-remove')
        self.client.login(username=self.user.username, password='test')
        response = self.client.delete(
            url, json.dumps({'track': self.track.pk}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(TrackFavorite.objects.count(), 0)

    from funkwhale_api.users.models import User

    def test_can_restrict_api_views_to_authenticated_users(self):
        urls = [
            ('api:v1:favorites:tracks-list', 'get'),
        ]

        for route_name, method in urls:
            url = self.reverse(route_name)
            with self.settings(API_AUTHENTICATION_REQUIRED=True):
                response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 401)

        self.client.login(username=self.user.username, password='test')

        for route_name, method in urls:
            url = self.reverse(route_name)
            with self.settings(API_AUTHENTICATION_REQUIRED=False):
                response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 200)

    def test_can_filter_tracks_by_favorites(self):
        favorite = TrackFavorite.add(self.track, self.user)

        url = reverse('api:v1:tracks-list')
        self.client.login(username=self.user.username, password='test')

        response = self.client.get(url, data={'favorites': True})

        parsed_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed_json['count'], 1)
        self.assertEqual(parsed_json['results'][0]['id'], self.track.id)
