import os

import factory

from funkwhale_api.factories import ManyToManyFromList, registry, NoUpdateOnCreate

from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.music import licenses
from funkwhale_api.users import factories as users_factories

SAMPLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tests",
    "music",
)


def playable_factory(field):
    @factory.post_generation
    def inner(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            UploadFactory(
                library__privacy_level="everyone",
                import_status="finished",
                **{field: self}
            )

    return inner


def deduce_from_conf(field):
    @factory.lazy_attribute
    def inner(self):
        return licenses.LICENSES_BY_ID[self.code][field]

    return inner


@registry.register
class LicenseFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    code = "cc-by-4.0"
    url = deduce_from_conf("url")
    commercial = deduce_from_conf("commercial")
    redistribute = deduce_from_conf("redistribute")
    copyleft = deduce_from_conf("copyleft")
    attribution = deduce_from_conf("attribution")
    derivative = deduce_from_conf("derivative")

    class Meta:
        model = "music.License"
        django_get_or_create = ("code",)


@registry.register
class ArtistFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    mbid = factory.Faker("uuid4")
    fid = factory.Faker("federation_url")
    playable = playable_factory("track__album__artist")

    class Meta:
        model = "music.Artist"

    class Params:
        attributed = factory.Trait(
            attributed_to=factory.SubFactory(federation_factories.ActorFactory)
        )
        local = factory.Trait(fid=factory.Faker("federation_url", local=True))


@registry.register
class AlbumFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=3)
    mbid = factory.Faker("uuid4")
    release_date = factory.Faker("date_object")
    cover = factory.django.ImageField()
    artist = factory.SubFactory(ArtistFactory)
    release_group_id = factory.Faker("uuid4")
    fid = factory.Faker("federation_url")
    playable = playable_factory("track__album")

    class Meta:
        model = "music.Album"

    class Params:
        attributed = factory.Trait(
            attributed_to=factory.SubFactory(federation_factories.ActorFactory)
        )

        local = factory.Trait(
            fid=factory.Faker("federation_url", local=True), artist__local=True
        )


@registry.register
class TrackFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    fid = factory.Faker("federation_url")
    title = factory.Faker("sentence", nb_words=3)
    mbid = factory.Faker("uuid4")
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SelfAttribute("album.artist")
    position = 1
    tags = ManyToManyFromList("tags")
    playable = playable_factory("track")

    class Meta:
        model = "music.Track"

    class Params:
        attributed = factory.Trait(
            attributed_to=factory.SubFactory(federation_factories.ActorFactory)
        )

        local = factory.Trait(
            fid=factory.Faker("federation_url", local=True), album__local=True
        )

    @factory.post_generation
    def license(self, created, extracted, **kwargs):
        if not created:
            return

        if extracted:
            self.license = LicenseFactory(code=extracted)
            self.save()


@registry.register
class UploadFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
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
        in_place = factory.Trait(audio_file=None, mimetype=None)
        playable = factory.Trait(
            import_status="finished", library__privacy_level="everyone"
        )


@registry.register
class UploadVersionFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    upload = factory.SubFactory(UploadFactory, bitrate=200000)
    bitrate = factory.SelfAttribute("upload.bitrate")
    mimetype = "audio/mpeg"
    audio_file = factory.django.FileField()
    size = 2000000

    class Meta:
        model = "music.UploadVersion"


@registry.register
class TagFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.SelfAttribute("slug")
    slug = factory.Faker("slug")

    class Meta:
        model = "taggit.Tag"


# XXX To remove


class ImportBatchFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    submitted_by = factory.SubFactory(users_factories.UserFactory)

    class Meta:
        model = "music.ImportBatch"


@registry.register
class ImportJobFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    batch = factory.SubFactory(ImportBatchFactory)
    source = factory.Faker("url")
    mbid = factory.Faker("uuid4")
    replace_if_duplicate = False

    class Meta:
        model = "music.ImportJob"
