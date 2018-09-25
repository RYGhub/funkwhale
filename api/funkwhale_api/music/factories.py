import os

import factory

from funkwhale_api.factories import ManyToManyFromList, registry
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.users import factories as users_factories


SAMPLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tests",
    "music",
)


@registry.register
class ArtistFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    mbid = factory.Faker("uuid4")
    fid = factory.Faker("federation_url")

    class Meta:
        model = "music.Artist"


@registry.register
class AlbumFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=3)
    mbid = factory.Faker("uuid4")
    release_date = factory.Faker("date_object")
    cover = factory.django.ImageField()
    artist = factory.SubFactory(ArtistFactory)
    release_group_id = factory.Faker("uuid4")
    fid = factory.Faker("federation_url")

    class Meta:
        model = "music.Album"


@registry.register
class TrackFactory(factory.django.DjangoModelFactory):
    fid = factory.Faker("federation_url")
    title = factory.Faker("sentence", nb_words=3)
    mbid = factory.Faker("uuid4")
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SelfAttribute("album.artist")
    position = 1
    tags = ManyToManyFromList("tags")

    class Meta:
        model = "music.Track"


@registry.register
class UploadFactory(factory.django.DjangoModelFactory):
    fid = factory.Faker("federation_url")
    track = factory.SubFactory(TrackFactory)
    library = factory.SubFactory(federation_factories.MusicLibraryFactory)
    audio_file = factory.django.FileField(
        from_path=os.path.join(SAMPLES_PATH, "test.ogg")
    )

    bitrate = None
    size = None
    duration = None
    mimetype = "audio/ogg"

    class Meta:
        model = "music.Upload"

    class Params:
        in_place = factory.Trait(audio_file=None)


@registry.register
class WorkFactory(factory.django.DjangoModelFactory):
    mbid = factory.Faker("uuid4")
    language = "eng"
    nature = "song"
    title = factory.Faker("sentence", nb_words=3)

    class Meta:
        model = "music.Work"


@registry.register
class LyricsFactory(factory.django.DjangoModelFactory):
    work = factory.SubFactory(WorkFactory)
    url = factory.Faker("url")
    content = factory.Faker("paragraphs", nb=4)

    class Meta:
        model = "music.Lyrics"


@registry.register
class TagFactory(factory.django.DjangoModelFactory):
    name = factory.SelfAttribute("slug")
    slug = factory.Faker("slug")

    class Meta:
        model = "taggit.Tag"


# XXX To remove


class ImportBatchFactory(factory.django.DjangoModelFactory):
    submitted_by = factory.SubFactory(users_factories.UserFactory)

    class Meta:
        model = "music.ImportBatch"


@registry.register
class ImportJobFactory(factory.django.DjangoModelFactory):
    batch = factory.SubFactory(ImportBatchFactory)
    source = factory.Faker("url")
    mbid = factory.Faker("uuid4")
    replace_if_duplicate = False

    class Meta:
        model = "music.ImportJob"
