import factory
import os

from funkwhale_api.users.tests.factories import UserFactory

SAMPLES_PATH = os.path.dirname(os.path.abspath(__file__))


class ArtistFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    mbid = factory.Faker('uuid4')

    class Meta:
        model = 'music.Artist'


class AlbumFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    mbid = factory.Faker('uuid4')
    release_date = factory.Faker('date')
    cover = factory.django.ImageField()
    artist = factory.SubFactory(ArtistFactory)
    release_group_id = factory.Faker('uuid4')

    class Meta:
        model = 'music.Album'


class TrackFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    mbid = factory.Faker('uuid4')
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SelfAttribute('album.artist')
    position = 1

    class Meta:
        model = 'music.Track'


class TrackFileFactory(factory.django.DjangoModelFactory):
    track = factory.SubFactory(TrackFactory)
    audio_file = factory.django.FileField(
        from_path=os.path.join(SAMPLES_PATH, 'test.ogg'))

    class Meta:
        model = 'music.TrackFile'


class ImportBatchFactory(factory.django.DjangoModelFactory):
    submitted_by = factory.SubFactory(UserFactory)

    class Meta:
        model = 'music.ImportBatch'


class ImportJobFactory(factory.django.DjangoModelFactory):
    batch = factory.SubFactory(ImportBatchFactory)
    source = factory.Faker('url')

    class Meta:
        model = 'music.ImportJob'
