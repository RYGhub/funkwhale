import factory
import requests
import requests_http_signature
import uuid

from django.utils import timezone
from django.conf import settings

from funkwhale_api.factories import registry

from . import keys
from . import models


registry.register(keys.get_key_pair, name='federation.KeyPair')


@registry.register(name='federation.SignatureAuth')
class SignatureAuthFactory(factory.Factory):
    algorithm = 'rsa-sha256'
    key = factory.LazyFunction(lambda: keys.get_key_pair()[0])
    key_id = factory.Faker('url')
    use_auth_header = False
    headers = [
        '(request-target)',
        'user-agent',
        'host',
        'date',
        'content-type',]
    class Meta:
        model = requests_http_signature.HTTPSignatureAuth


@registry.register(name='federation.SignedRequest')
class SignedRequestFactory(factory.Factory):
    url = factory.Faker('url')
    method = 'get'
    auth = factory.SubFactory(SignatureAuthFactory)

    class Meta:
        model = requests.Request

    @factory.post_generation
    def headers(self, create, extracted, **kwargs):
        default_headers = {
            'User-Agent': 'Test',
            'Host': 'test.host',
            'Date': 'Right now',
            'Content-Type': 'application/activity+json'
        }
        if extracted:
            default_headers.update(extracted)
        self.headers.update(default_headers)


@registry.register(name='federation.Link')
class LinkFactory(factory.Factory):
    type = 'Link'
    href = factory.Faker('url')
    mediaType = 'text/html'

    class Meta:
        model = dict

    class Params:
        audio = factory.Trait(
            mediaType=factory.Iterator(['audio/mp3', 'audio/ogg'])
        )


@registry.register
class ActorFactory(factory.DjangoModelFactory):
    public_key = None
    private_key = None
    preferred_username = factory.Faker('user_name')
    summary = factory.Faker('paragraph')
    domain = factory.Faker('domain_name')
    url = factory.LazyAttribute(lambda o: 'https://{}/users/{}'.format(o.domain, o.preferred_username))
    inbox_url = factory.LazyAttribute(lambda o: 'https://{}/users/{}/inbox'.format(o.domain, o.preferred_username))
    outbox_url = factory.LazyAttribute(lambda o: 'https://{}/users/{}/outbox'.format(o.domain, o.preferred_username))

    class Meta:
        model = models.Actor

    class Params:
        local = factory.Trait(
            domain=factory.LazyAttribute(
                lambda o: settings.FEDERATION_HOSTNAME)
        )

    @classmethod
    def _generate(cls, create, attrs):
        has_public = attrs.get('public_key') is not None
        has_private = attrs.get('private_key') is not None
        if not has_public and not has_private:
            private, public = keys.get_key_pair()
            attrs['private_key'] = private.decode('utf-8')
            attrs['public_key'] = public.decode('utf-8')
        return super()._generate(create, attrs)


@registry.register
class FollowFactory(factory.DjangoModelFactory):
    target = factory.SubFactory(ActorFactory)
    actor = factory.SubFactory(ActorFactory)

    class Meta:
        model = models.Follow

    class Params:
        local = factory.Trait(
            actor=factory.SubFactory(ActorFactory, local=True)
        )


@registry.register
class FollowRequestFactory(factory.DjangoModelFactory):
    target = factory.SubFactory(ActorFactory)
    actor = factory.SubFactory(ActorFactory)

    class Meta:
        model = models.FollowRequest


@registry.register
class LibraryFactory(factory.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    url = factory.Faker('url')
    federation_enabled = True
    download_files = False
    autoimport = False

    class Meta:
        model = models.Library


class ArtistMetadataFactory(factory.Factory):
    name = factory.Faker('name')

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(
            musicbrainz_id=factory.Faker('uuid4')
        )


class ReleaseMetadataFactory(factory.Factory):
    title = factory.Faker('sentence')

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(
            musicbrainz_id=factory.Faker('uuid4')
        )


class RecordingMetadataFactory(factory.Factory):
    title = factory.Faker('sentence')

    class Meta:
        model = dict

    class Params:
        musicbrainz = factory.Trait(
            musicbrainz_id=factory.Faker('uuid4')
        )


@registry.register(name='federation.LibraryTrackMetadata')
class LibraryTrackMetadataFactory(factory.Factory):
    artist = factory.SubFactory(ArtistMetadataFactory)
    recording = factory.SubFactory(RecordingMetadataFactory)
    release = factory.SubFactory(ReleaseMetadataFactory)

    class Meta:
        model = dict


@registry.register
class LibraryTrackFactory(factory.DjangoModelFactory):
    library = factory.SubFactory(LibraryFactory)
    url = factory.Faker('url')
    title = factory.Faker('sentence')
    artist_name = factory.Faker('sentence')
    album_title = factory.Faker('sentence')
    audio_url = factory.Faker('url')
    audio_mimetype = 'audio/ogg'
    metadata = factory.SubFactory(LibraryTrackMetadataFactory)

    class Meta:
        model = models.LibraryTrack


@registry.register(name='federation.Note')
class NoteFactory(factory.Factory):
    type = 'Note'
    id = factory.Faker('url')
    published = factory.LazyFunction(
        lambda: timezone.now().isoformat()
    )
    inReplyTo = None
    content = factory.Faker('sentence')

    class Meta:
        model = dict


@registry.register(name='federation.Activity')
class ActivityFactory(factory.Factory):
    type = 'Create'
    id = factory.Faker('url')
    published = factory.LazyFunction(
        lambda: timezone.now().isoformat()
    )
    actor = factory.Faker('url')
    object = factory.SubFactory(
        NoteFactory,
        actor=factory.SelfAttribute('..actor'),
        published=factory.SelfAttribute('..published'))

    class Meta:
        model = dict


@registry.register(name='federation.AudioMetadata')
class AudioMetadataFactory(factory.Factory):
    recording = factory.LazyAttribute(
        lambda o: 'https://musicbrainz.org/recording/{}'.format(uuid.uuid4())
    )
    artist = factory.LazyAttribute(
        lambda o: 'https://musicbrainz.org/artist/{}'.format(uuid.uuid4())
    )
    release = factory.LazyAttribute(
        lambda o: 'https://musicbrainz.org/release/{}'.format(uuid.uuid4())
    )

    class Meta:
        model = dict


@registry.register(name='federation.Audio')
class AudioFactory(factory.Factory):
    type = 'Audio'
    id = factory.Faker('url')
    published = factory.LazyFunction(
        lambda: timezone.now().isoformat()
    )
    actor = factory.Faker('url')
    url = factory.SubFactory(LinkFactory, audio=True)
    metadata = factory.SubFactory(LibraryTrackMetadataFactory)

    class Meta:
        model = dict
