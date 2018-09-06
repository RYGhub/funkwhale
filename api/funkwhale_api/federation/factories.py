import uuid

import factory
import requests
import requests_http_signature
from django.conf import settings
from django.utils import timezone
from django.utils.http import http_date

from funkwhale_api.factories import registry
from funkwhale_api.users import factories as user_factories

from . import keys, models

registry.register(keys.get_key_pair, name="federation.KeyPair")


@registry.register(name="federation.SignatureAuth")
class SignatureAuthFactory(factory.Factory):
    algorithm = "rsa-sha256"
    key = factory.LazyFunction(lambda: keys.get_key_pair()[0])
    key_id = factory.Faker("url")
    use_auth_header = False
    headers = ["(request-target)", "user-agent", "host", "date", "content-type"]

    class Meta:
        model = requests_http_signature.HTTPSignatureAuth


@registry.register(name="federation.SignedRequest")
class SignedRequestFactory(factory.Factory):
    url = factory.Faker("url")
    method = "get"
    auth = factory.SubFactory(SignatureAuthFactory)

    class Meta:
        model = requests.Request

    @factory.post_generation
    def headers(self, create, extracted, **kwargs):
        default_headers = {
            "User-Agent": "Test",
            "Host": "test.host",
            "Date": http_date(timezone.now().timestamp()),
            "Content-Type": "application/activity+json",
        }
        if extracted:
            default_headers.update(extracted)
        self.headers.update(default_headers)


@registry.register(name="federation.Link")
class LinkFactory(factory.Factory):
    type = "Link"
    href = factory.Faker("url")
    mediaType = "text/html"

    class Meta:
        model = dict

    class Params:
        audio = factory.Trait(mediaType=factory.Iterator(["audio/mp3", "audio/ogg"]))


def create_user(actor):
    return user_factories.UserFactory(actor=actor)


@registry.register
class ActorFactory(factory.DjangoModelFactory):
    public_key = None
    private_key = None
    preferred_username = factory.Faker("user_name")
    summary = factory.Faker("paragraph")
    domain = factory.Faker("domain_name")
    fid = factory.LazyAttribute(
        lambda o: "https://{}/users/{}".format(o.domain, o.preferred_username)
    )
    inbox_url = factory.LazyAttribute(
        lambda o: "https://{}/users/{}/inbox".format(o.domain, o.preferred_username)
    )
    outbox_url = factory.LazyAttribute(
        lambda o: "https://{}/users/{}/outbox".format(o.domain, o.preferred_username)
    )

    class Meta:
        model = models.Actor

    @factory.post_generation
    def local(self, create, extracted, **kwargs):
        if not extracted and not kwargs:
            return
        from funkwhale_api.users.factories import UserFactory

        self.domain = settings.FEDERATION_HOSTNAME
        self.save(update_fields=["domain"])
        if not create:
            if extracted and hasattr(extracted, "pk"):
                extracted.actor = self
            else:
                UserFactory.build(actor=self, **kwargs)
        if extracted and hasattr(extracted, "pk"):
            extracted.actor = self
            extracted.save(update_fields=["user"])
        else:
            self.user = UserFactory(actor=self, **kwargs)

    @factory.post_generation
    def keys(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if not extracted:
            private, public = keys.get_key_pair()
            self.private_key = private.decode("utf-8")
            self.public_key = public.decode("utf-8")


@registry.register
class FollowFactory(factory.DjangoModelFactory):
    target = factory.SubFactory(ActorFactory)
    actor = factory.SubFactory(ActorFactory)

    class Meta:
        model = models.Follow

    class Params:
        local = factory.Trait(actor=factory.SubFactory(ActorFactory, local=True))


@registry.register
class MusicLibraryFactory(factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    privacy_level = "me"
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    files_count = 0

    class Meta:
        model = "music.Library"

    @factory.post_generation
    def fid(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.fid = extracted or self.get_federation_id()

    @factory.post_generation
    def followers_url(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.followers_url = extracted or self.fid + "/followers"


@registry.register
class LibraryScan(factory.django.DjangoModelFactory):
    library = factory.SubFactory(MusicLibraryFactory)
    actor = factory.SubFactory(ActorFactory)
    total_files = factory.LazyAttribute(lambda o: o.library.files_count)

    class Meta:
        model = "music.LibraryScan"


@registry.register
class ActivityFactory(factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    url = factory.Faker("url")
    payload = factory.LazyFunction(lambda: {"type": "Create"})

    class Meta:
        model = "federation.Activity"


@registry.register
class InboxItemFactory(factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    activity = factory.SubFactory(ActivityFactory)
    type = "to"

    class Meta:
        model = "federation.InboxItem"


@registry.register
class LibraryFollowFactory(factory.DjangoModelFactory):
    target = factory.SubFactory(MusicLibraryFactory)
    actor = factory.SubFactory(ActorFactory)

    class Meta:
        model = "federation.LibraryFollow"


class ArtistMetadataFactory(factory.Factory):
    name = factory.Faker("name")

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(musicbrainz_id=factory.Faker("uuid4"))


class ReleaseMetadataFactory(factory.Factory):
    title = factory.Faker("sentence")

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(musicbrainz_id=factory.Faker("uuid4"))


class RecordingMetadataFactory(factory.Factory):
    title = factory.Faker("sentence")

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(musicbrainz_id=factory.Faker("uuid4"))


@registry.register(name="federation.LibraryTrackMetadata")
class LibraryTrackMetadataFactory(factory.Factory):
    artist = factory.SubFactory(ArtistMetadataFactory)
    recording = factory.SubFactory(RecordingMetadataFactory)
    release = factory.SubFactory(ReleaseMetadataFactory)

    class Meta:
        model = dict


@registry.register(name="federation.Note")
class NoteFactory(factory.Factory):
    type = "Note"
    id = factory.Faker("url")
    published = factory.LazyFunction(lambda: timezone.now().isoformat())
    inReplyTo = None
    content = factory.Faker("sentence")

    class Meta:
        model = dict


@registry.register(name="federation.AudioMetadata")
class AudioMetadataFactory(factory.Factory):
    recording = factory.LazyAttribute(
        lambda o: "https://musicbrainz.org/recording/{}".format(uuid.uuid4())
    )
    artist = factory.LazyAttribute(
        lambda o: "https://musicbrainz.org/artist/{}".format(uuid.uuid4())
    )
    release = factory.LazyAttribute(
        lambda o: "https://musicbrainz.org/release/{}".format(uuid.uuid4())
    )
    bitrate = 42
    length = 43
    size = 44

    class Meta:
        model = dict


@registry.register(name="federation.Audio")
class AudioFactory(factory.Factory):
    type = "Audio"
    id = factory.Faker("url")
    published = factory.LazyFunction(lambda: timezone.now().isoformat())
    actor = factory.Faker("url")
    url = factory.SubFactory(LinkFactory, audio=True)
    metadata = factory.SubFactory(LibraryTrackMetadataFactory)

    class Meta:
        model = dict
