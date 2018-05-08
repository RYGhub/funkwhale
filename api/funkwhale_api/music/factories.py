import factory
import os

from funkwhale_api.factories import registry, ManyToManyFromList
from funkwhale_api.federation.factories import (
    LibraryTrackFactory,
)
from funkwhale_api.users.factories import UserFactory

SAMPLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'tests', 'music'
)


@registry.register
class ArtistFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    mbid = factory.Faker('uuid4')

    class Meta:
        model = 'music.Artist'


@registry.register
class AlbumFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    mbid = factory.Faker('uuid4')
    release_date = factory.Faker('date_object')
    cover = factory.django.ImageField()
    artist = factory.SubFactory(ArtistFactory)
    release_group_id = factory.Faker('uuid4')

    class Meta:
        model = 'music.Album'


@registry.register
class TrackFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    mbid = factory.Faker('uuid4')
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SelfAttribute('album.artist')
    position = 1
    tags = ManyToManyFromList('tags')

    class Meta:
        model = 'music.Track'


@registry.register
class TrackFileFactory(factory.django.DjangoModelFactory):
    track = factory.SubFactory(TrackFactory)
    audio_file = factory.django.FileField(
        from_path=os.path.join(SAMPLES_PATH, 'test.ogg'))

    class Meta:
        model = 'music.TrackFile'

    class Params:
        in_place = factory.Trait(
            audio_file=None,
        )
        federation = factory.Trait(
            audio_file=None,
            library_track=factory.SubFactory(LibraryTrackFactory),
            mimetype=factory.LazyAttribute(
                lambda o: o.library_track.audio_mimetype
            ),
            source=factory.LazyAttribute(
                lambda o: o.library_track.audio_url
            ),
        )


@registry.register
class ImportBatchFactory(factory.django.DjangoModelFactory):
    submitted_by = factory.SubFactory(UserFactory)

    class Meta:
        model = 'music.ImportBatch'

    class Params:
        federation = factory.Trait(
            submitted_by=None,
            source='federation',
        )
        finished = factory.Trait(
            status='finished',
        )


@registry.register
class ImportJobFactory(factory.django.DjangoModelFactory):
    batch = factory.SubFactory(ImportBatchFactory)
    source = factory.Faker('url')
    mbid = factory.Faker('uuid4')

    class Meta:
        model = 'music.ImportJob'

    class Params:
        federation = factory.Trait(
            mbid=None,
            library_track=factory.SubFactory(LibraryTrackFactory),
            batch=factory.SubFactory(ImportBatchFactory, federation=True),
        )
        finished = factory.Trait(
            status='finished',
            track_file=factory.SubFactory(TrackFileFactory),
        )
        in_place = factory.Trait(
            status='finished',
            audio_file=None,
        )


@registry.register(name='music.FileImportJob')
class FileImportJobFactory(ImportJobFactory):
    source = 'file://'
    mbid = None
    audio_file = factory.django.FileField(
        from_path=os.path.join(SAMPLES_PATH, 'test.ogg'))


@registry.register
class WorkFactory(factory.django.DjangoModelFactory):
    mbid = factory.Faker('uuid4')
    language = 'eng'
    nature = 'song'
    title = factory.Faker('sentence', nb_words=3)

    class Meta:
        model = 'music.Work'


@registry.register
class LyricsFactory(factory.django.DjangoModelFactory):
    work = factory.SubFactory(WorkFactory)
    url = factory.Faker('url')
    content = factory.Faker('paragraphs', nb=4)

    class Meta:
        model = 'music.Lyrics'


@registry.register
class TagFactory(factory.django.DjangoModelFactory):
    name = factory.SelfAttribute('slug')
    slug = factory.Faker('slug')

    class Meta:
        model = 'taggit.Tag'
