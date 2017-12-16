from test_plus.test import TestCase
import unittest.mock
from funkwhale_api.music import models
import datetime

from . import factories
from . import data as api_data
from .cover import binary_data


class TestMusic(TestCase):

    @unittest.mock.patch('musicbrainzngs.search_artists', return_value=api_data.artists['search']['adhesive_wombat'])
    def test_can_create_artist_from_api(self, *mocks):
        artist = models.Artist.create_from_api(query="Adhesive wombat")
        data = models.Artist.api.search(query='Adhesive wombat')['artist-list'][0]

        self.assertEqual(int(data['ext:score']), 100)
        self.assertEqual(data['id'], '62c3befb-6366-4585-b256-809472333801')
        self.assertEqual(artist.mbid, data['id'])
        self.assertEqual(artist.name, 'Adhesive Wombat')

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.search', return_value=api_data.albums['search']['hypnotize'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['soad'])
    def test_can_create_album_from_api(self, *mocks):
        album = models.Album.create_from_api(query="Hypnotize", artist='system of a down', type='album')
        data = models.Album.api.search(query='Hypnotize', artist='system of a down', type='album')['release-list'][0]

        self.assertEqual(album.mbid, data['id'])
        self.assertEqual(album.title, 'Hypnotize')
        with self.assertRaises(ValueError):
            self.assertFalse(album.cover.path is None)
        self.assertEqual(album.release_date, datetime.date(2005, 1, 1))
        self.assertEqual(album.artist.name, 'System of a Down')
        self.assertEqual(album.artist.mbid, data['artist-credit'][0]['artist']['id'])

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['adhesive_wombat'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get']['marsupial'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.search', return_value=api_data.tracks['search']['8bitadventures'])
    def test_can_create_track_from_api(self, *mocks):
        track = models.Track.create_from_api(query="8-bit adventure")
        data = models.Track.api.search(query='8-bit adventure')['recording-list'][0]
        self.assertEqual(int(data['ext:score']), 100)
        self.assertEqual(data['id'], '9968a9d6-8d92-4051-8f76-674e157b6eed')
        self.assertEqual(track.mbid, data['id'])
        self.assertTrue(track.artist.pk is not None)
        self.assertEqual(str(track.artist.mbid), '62c3befb-6366-4585-b256-809472333801')
        self.assertEqual(track.artist.name, 'Adhesive Wombat')
        self.assertEqual(str(track.album.mbid), 'a50d2a81-2a50-484d-9cb4-b9f6833f583e')
        self.assertEqual(track.album.title, 'Marsupial Madness')

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['adhesive_wombat'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get']['marsupial'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.get', return_value=api_data.tracks['get']['8bitadventures'])
    def test_can_create_track_from_api_with_corresponding_tags(self, *mocks):
        track = models.Track.create_from_api(id='9968a9d6-8d92-4051-8f76-674e157b6eed')
        expected_tags = ['techno', 'good-music']
        track_tags = [tag.slug for tag in track.tags.all()]
        for tag in expected_tags:
            self.assertIn(tag, track_tags)

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['adhesive_wombat'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get']['marsupial'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.search', return_value=api_data.tracks['search']['8bitadventures'])
    def test_can_get_or_create_track_from_api(self, *mocks):
        track = models.Track.create_from_api(query="8-bit adventure")
        data = models.Track.api.search(query='8-bit adventure')['recording-list'][0]
        self.assertEqual(int(data['ext:score']), 100)
        self.assertEqual(data['id'], '9968a9d6-8d92-4051-8f76-674e157b6eed')
        self.assertEqual(track.mbid, data['id'])
        self.assertTrue(track.artist.pk is not None)
        self.assertEqual(str(track.artist.mbid), '62c3befb-6366-4585-b256-809472333801')
        self.assertEqual(track.artist.name, 'Adhesive Wombat')

        track2, created = models.Track.get_or_create_from_api(mbid=data['id'])
        self.assertFalse(created)
        self.assertEqual(track, track2)

    def test_album_tags_deduced_from_tracks_tags(self):
        tag = factories.TagFactory()
        album = factories.AlbumFactory()
        tracks = factories.TrackFactory.create_batch(album=album, size=5)

        for track in tracks:
            track.tags.add(tag)

        album = models.Album.objects.prefetch_related('tracks__tags').get(pk=album.pk)

        with self.assertNumQueries(0):
            self.assertIn(tag, album.tags)

    def test_artist_tags_deduced_from_album_tags(self):
        tag = factories.TagFactory()
        artist = factories.ArtistFactory()
        album = factories.AlbumFactory(artist=artist)
        tracks = factories.TrackFactory.create_batch(album=album, size=5)

        for track in tracks:
            track.tags.add(tag)

        artist = models.Artist.objects.prefetch_related('albums__tracks__tags').get(pk=artist.pk)

        with self.assertNumQueries(0):
            self.assertIn(tag, artist.tags)

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.images.get_front', return_value=binary_data)
    def test_can_download_image_file_for_album(self, *mocks):
        # client._api.get_image_front('55ea4f82-b42b-423e-a0e5-290ccdf443ed')
        album = factories.AlbumFactory(mbid='55ea4f82-b42b-423e-a0e5-290ccdf443ed')
        album.get_image()
        album.save()

        self.assertEqual(album.cover.file.read(), binary_data)
