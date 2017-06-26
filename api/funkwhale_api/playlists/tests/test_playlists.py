import json
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from model_mommy import mommy

from funkwhale_api.users.models import User
from funkwhale_api.playlists import models
from funkwhale_api.playlists.serializers import PlaylistSerializer


class TestPlayLists(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test')

    def test_can_create_playlist(self):
        tracks = list(mommy.make('music.Track', _quantity=5))
        playlist = models.Playlist.objects.create(user=self.user, name="test")

        previous = None
        for i in range(len(tracks)):
            previous = playlist.add_track(tracks[i], previous=previous)

        playlist_tracks = list(playlist.playlist_tracks.all())

        previous = None
        for idx, track in enumerate(tracks):
            plt = playlist_tracks[idx]
            self.assertEqual(plt.position, idx)
            self.assertEqual(plt.track, track)
            if previous:
                self.assertEqual(playlist_tracks[idx + 1], previous)
            self.assertEqual(plt.playlist, playlist)

    def test_can_create_playlist_via_api(self):
        self.client.login(username=self.user.username, password='test')
        url = reverse('api:v1:playlists-list')
        data = {
            'name': 'test',
        }

        response = self.client.post(url, data)

        playlist = self.user.playlists.latest('id')
        self.assertEqual(playlist.name, 'test')

    def test_can_add_playlist_track_via_api(self):
        tracks = list(mommy.make('music.Track', _quantity=5))
        playlist = models.Playlist.objects.create(user=self.user, name="test")

        self.client.login(username=self.user.username, password='test')

        url = reverse('api:v1:playlist-tracks-list')
        data = {
            'playlist': playlist.pk,
            'track': tracks[0].pk
        }

        response = self.client.post(url, data)
        plts = self.user.playlists.latest('id').playlist_tracks.all()
        self.assertEqual(plts.first().track, tracks[0])
