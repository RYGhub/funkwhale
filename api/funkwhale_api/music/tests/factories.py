import factory


class ArtistFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'artist-{0}'.format(n))
    mbid = factory.Faker('uuid4')

    class Meta:
        model = 'music.Artist'


class AlbumFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'album-{0}'.format(n))
    mbid = factory.Faker('uuid4')
    release_date = factory.Faker('date')
    cover = factory.django.ImageField()
    artist = factory.SubFactory(ArtistFactory)

    class Meta:
        model = 'music.Album'


class TrackFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'track-{0}'.format(n))
    mbid = factory.Faker('uuid4')
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SelfAttribute('album.artist')
    position = 1

    class Meta:
        model = 'music.Track'


class TrackFileFactory(factory.django.DjangoModelFactory):
    track = factory.SubFactory(TrackFactory)
    audio_file = factory.django.FileField()

    class Meta:
        model = 'music.TrackFile'
