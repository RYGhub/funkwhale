import urllib.parse

from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction

from rest_framework import serializers
from dynamic_preferences.registries import global_preferences_registry

from funkwhale_api.common import utils as funkwhale_utils

from . import activity
from . import models
from . import utils


AP_CONTEXT = [
    'https://www.w3.org/ns/activitystreams',
    'https://w3id.org/security/v1',
    {},
]


class ActorSerializer(serializers.ModelSerializer):
    # left maps to activitypub fields, right to our internal models
    id = serializers.URLField(source='url')
    outbox = serializers.URLField(source='outbox_url')
    inbox = serializers.URLField(source='inbox_url')
    following = serializers.URLField(
        source='following_url', required=False, allow_null=True)
    followers = serializers.URLField(
        source='followers_url', required=False, allow_null=True)
    preferredUsername = serializers.CharField(
        source='preferred_username', required=False)
    publicKey = serializers.JSONField(source='public_key', required=False)
    manuallyApprovesFollowers = serializers.NullBooleanField(
        source='manually_approves_followers', required=False)
    summary = serializers.CharField(max_length=None, required=False)

    class Meta:
        model = models.Actor
        fields = [
            'id',
            'type',
            'name',
            'summary',
            'preferredUsername',
            'publicKey',
            'inbox',
            'outbox',
            'following',
            'followers',
            'manuallyApprovesFollowers',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['@context'] = AP_CONTEXT
        if instance.public_key:
            ret['publicKey'] = {
                'owner': instance.url,
                'publicKeyPem': instance.public_key,
                'id': '{}#main-key'.format(instance.url)
            }
        ret['endpoints'] = {}
        if instance.shared_inbox_url:
            ret['endpoints']['sharedInbox'] = instance.shared_inbox_url
        return ret

    def prepare_missing_fields(self):
        kwargs = {}
        domain = urllib.parse.urlparse(self.validated_data['url']).netloc
        kwargs['domain'] = domain
        for endpoint, url in self.initial_data.get('endpoints', {}).items():
            if endpoint == 'sharedInbox':
                kwargs['shared_inbox_url'] = url
                break
        try:
            kwargs['public_key'] = self.initial_data['publicKey']['publicKeyPem']
        except KeyError:
            pass
        return kwargs

    def build(self):
        d = self.validated_data.copy()
        d.update(self.prepare_missing_fields())
        return self.Meta.model(**d)

    def save(self, **kwargs):
        kwargs.update(self.prepare_missing_fields())
        return super().save(**kwargs)

    def validate_summary(self, value):
        if value:
            return value[:500]


class LibraryActorSerializer(ActorSerializer):
    url = serializers.ListField(
        child=serializers.JSONField())

    class Meta(ActorSerializer.Meta):
        fields = ActorSerializer.Meta.fields + ['url']

    def validate(self, validated_data):
        try:
            urls = validated_data['url']
        except KeyError:
            raise serializers.ValidationError('Missing URL field')

        for u in urls:
            try:
                if u['name'] != 'library':
                    continue
                validated_data['library_url'] = u['href']
                break
            except KeyError:
                continue

        return validated_data


class APILibraryCreateSerializer(serializers.ModelSerializer):
    actor = serializers.URLField()

    class Meta:
        model = models.Library
        fields = [
            'actor',
            'autoimport',
            'federation_enabled',
            'download_files',
        ]

    def validate(self, validated_data):
        from . import actors
        from . import library

        actor_url = validated_data['actor']
        actor_data = actors.get_actor_data(actor_url)
        acs = LibraryActorSerializer(data=actor_data)
        acs.is_valid(raise_exception=True)
        try:
            actor = models.Actor.objects.get(url=actor_url)
        except models.Actor.DoesNotExist:
            actor = acs.save()
        library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        validated_data['follow'] = models.Follow.objects.get_or_create(
            actor=library_actor,
            target=actor,
        )[0]
        if validated_data['follow'].approved is None:
            funkwhale_utils.on_commit(
                activity.deliver,
                FollowSerializer(validated_data['follow']).data,
                on_behalf_of=validated_data['follow'].actor,
                to=[validated_data['follow'].target.url],
            )

        library_data = library.get_library_data(
            acs.validated_data['library_url'])
        if 'errors' in library_data:
            raise serializers.ValidationError(str(library_data['errors']))
        validated_data['library'] = library_data
        validated_data['actor'] = actor
        return validated_data

    def create(self, validated_data):
        library = models.Library.objects.get_or_create(
            url=validated_data['library']['id'],
            defaults={
                'actor': validated_data['actor'],
                'follow': validated_data['follow'],
                'tracks_count': validated_data['library']['totalItems'],
                'federation_enabled': validated_data['federation_enabled'],
                'autoimport': validated_data['autoimport'],
                'download_files': validated_data['download_files'],
            }
        )[0]
        return library


class FollowSerializer(serializers.Serializer):
    id = serializers.URLField()
    object = serializers.URLField()
    actor = serializers.URLField()
    type = serializers.ChoiceField(choices=['Follow'])

    def validate_object(self, v):
        expected = self.context.get('follow_target')
        if expected and expected.url != v:
            raise serializers.ValidationError('Invalid target')
        try:
            return models.Actor.objects.get(url=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError('Target not found')

    def validate_actor(self, v):
        expected = self.context.get('follow_actor')
        if expected and expected.url != v:
            raise serializers.ValidationError('Invalid actor')
        try:
            return models.Actor.objects.get(url=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError('Actor not found')

    def save(self, **kwargs):
        return models.Follow.objects.get_or_create(
            actor=self.validated_data['actor'],
            target=self.validated_data['object'],
            **kwargs,
        )[0]

    def to_representation(self, instance):
        return {
            '@context': AP_CONTEXT,
            'actor': instance.actor.url,
            'id': instance.get_federation_url(),
            'object': instance.target.url,
            'type': 'Follow'
        }
        return ret


class APIFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Follow
        fields = [
            'uuid',
            'id',
            'approved',
            'creation_date',
            'modification_date',
            'actor',
            'target',
        ]


class AcceptFollowSerializer(serializers.Serializer):
    id = serializers.URLField()
    actor = serializers.URLField()
    object = FollowSerializer()
    type = serializers.ChoiceField(choices=['Accept'])

    def validate_actor(self, v):
        expected = self.context.get('follow_target')
        if expected and expected.url != v:
            raise serializers.ValidationError('Invalid actor')
        try:
            return models.Actor.objects.get(url=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError('Actor not found')

    def validate(self, validated_data):
        # we ensure the accept actor actually match the follow target
        if validated_data['actor'] != validated_data['object']['object']:
            raise serializers.ValidationError('Actor mismatch')
        try:
            validated_data['follow'] = models.Follow.objects.filter(
                target=validated_data['actor'],
                actor=validated_data['object']['actor']
            ).exclude(approved=True).get()
        except models.Follow.DoesNotExist:
            raise serializers.ValidationError('No follow to accept')
        return validated_data

    def to_representation(self, instance):
        return {
            "@context": AP_CONTEXT,
            "id": instance.get_federation_url() + '/accept',
            "type": "Accept",
            "actor": instance.target.url,
            "object": FollowSerializer(instance).data
        }

    def save(self):
        self.validated_data['follow'].approved = True
        self.validated_data['follow'].save()
        return self.validated_data['follow']


class UndoFollowSerializer(serializers.Serializer):
    id = serializers.URLField()
    actor = serializers.URLField()
    object = FollowSerializer()
    type = serializers.ChoiceField(choices=['Undo'])

    def validate_actor(self, v):
        expected = self.context.get('follow_target')
        if expected and expected.url != v:
            raise serializers.ValidationError('Invalid actor')
        try:
            return models.Actor.objects.get(url=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError('Actor not found')

    def validate(self, validated_data):
        # we ensure the accept actor actually match the follow actor
        if validated_data['actor'] != validated_data['object']['actor']:
            raise serializers.ValidationError('Actor mismatch')
        try:
            validated_data['follow'] = models.Follow.objects.filter(
                actor=validated_data['actor'],
                target=validated_data['object']['object']
            ).get()
        except models.Follow.DoesNotExist:
            raise serializers.ValidationError('No follow to remove')
        return validated_data

    def to_representation(self, instance):
        return {
            "@context": AP_CONTEXT,
            "id": instance.get_federation_url() + '/undo',
            "type": "Undo",
            "actor": instance.actor.url,
            "object": FollowSerializer(instance).data
        }

    def save(self):
        return self.validated_data['follow'].delete()


class ActorWebfingerSerializer(serializers.Serializer):
    subject = serializers.CharField()
    aliases = serializers.ListField(child=serializers.URLField())
    links = serializers.ListField()
    actor_url = serializers.URLField(required=False)

    def validate(self, validated_data):
        validated_data['actor_url'] = None
        for l in validated_data['links']:
            try:
                if not l['rel'] == 'self':
                    continue
                if not l['type'] == 'application/activity+json':
                    continue
                validated_data['actor_url'] = l['href']
                break
            except KeyError:
                pass
        if validated_data['actor_url'] is None:
            raise serializers.ValidationError('No valid actor url found')
        return validated_data

    def to_representation(self, instance):
        data = {}
        data['subject'] = 'acct:{}'.format(instance.webfinger_subject)
        data['links'] = [
            {
                'rel': 'self',
                'href': instance.url,
                'type': 'application/activity+json'
            }
        ]
        data['aliases'] = [
            instance.url
        ]
        return data


class ActivitySerializer(serializers.Serializer):
    actor = serializers.URLField()
    id = serializers.URLField()
    type = serializers.ChoiceField(
        choices=[(c, c) for c in activity.ACTIVITY_TYPES])
    object = serializers.JSONField()

    def validate_object(self, value):
        try:
            type = value['type']
        except KeyError:
            raise serializers.ValidationError('Missing object type')
        except TypeError:
            # probably a URL
            return value
        try:
            object_serializer = OBJECT_SERIALIZERS[type]
        except KeyError:
            raise serializers.ValidationError(
                'Unsupported type {}'.format(type))

        serializer = object_serializer(data=value)
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def validate_actor(self, value):
        request_actor = self.context.get('actor')
        if request_actor and request_actor.url != value:
            raise serializers.ValidationError(
                'The actor making the request do not match'
                ' the activity actor'
            )
        return value


class ObjectSerializer(serializers.Serializer):
    id = serializers.URLField()
    url = serializers.URLField(required=False, allow_null=True)
    type = serializers.ChoiceField(
        choices=[(c, c) for c in activity.OBJECT_TYPES])
    content = serializers.CharField(
        required=False, allow_null=True)
    summary = serializers.CharField(
        required=False, allow_null=True)
    name = serializers.CharField(
        required=False, allow_null=True)
    published = serializers.DateTimeField(
        required=False, allow_null=True)
    updated = serializers.DateTimeField(
        required=False, allow_null=True)
    to = serializers.ListField(
        child=serializers.URLField(),
        required=False, allow_null=True)
    cc = serializers.ListField(
        child=serializers.URLField(),
        required=False, allow_null=True)
    bto = serializers.ListField(
        child=serializers.URLField(),
        required=False, allow_null=True)
    bcc = serializers.ListField(
        child=serializers.URLField(),
        required=False, allow_null=True)

OBJECT_SERIALIZERS = {
    t: ObjectSerializer
    for t in activity.OBJECT_TYPES
}


class PaginatedCollectionSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['Collection'])
    totalItems = serializers.IntegerField(min_value=0)
    actor = serializers.URLField()
    id = serializers.URLField()

    def to_representation(self, conf):
        paginator = Paginator(
            conf['items'],
            conf.get('page_size', 20)
        )
        first = funkwhale_utils.set_query_parameter(conf['id'], page=1)
        current = first
        last = funkwhale_utils.set_query_parameter(
            conf['id'], page=paginator.num_pages)
        d = {
            'id': conf['id'],
            'actor': conf['actor'].url,
            'totalItems': paginator.count,
            'type': 'Collection',
            'current': current,
            'first': first,
            'last': last,
        }
        if self.context.get('include_ap_context', True):
            d['@context'] = AP_CONTEXT
        return d


class CollectionPageSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['CollectionPage'])
    totalItems = serializers.IntegerField(min_value=0)
    items = serializers.ListField()
    actor = serializers.URLField()
    id = serializers.URLField()
    prev = serializers.URLField(required=False)
    next = serializers.URLField(required=False)
    partOf = serializers.URLField()

    def to_representation(self, conf):
        page = conf['page']
        first = funkwhale_utils.set_query_parameter(
            conf['id'], page=1)
        last = funkwhale_utils.set_query_parameter(
            conf['id'], page=page.paginator.num_pages)
        id = funkwhale_utils.set_query_parameter(
            conf['id'], page=page.number)
        d = {
            'id': id,
            'partOf': conf['id'],
            'actor': conf['actor'].url,
            'totalItems': page.paginator.count,
            'type': 'CollectionPage',
            'first': first,
            'last': last,
            'items': [
                conf['item_serializer'](
                    i,
                    context={
                        'actor': conf['actor'],
                        'include_ap_context': False}
                ).data
                for i in page.object_list
            ]
        }

        if page.has_previous():
            d['prev'] = funkwhale_utils.set_query_parameter(
                conf['id'], page=page.previous_page_number())

        if page.has_next():
            d['next'] = funkwhale_utils.set_query_parameter(
                conf['id'], page=page.next_page_number())

        if self.context.get('include_ap_context', True):
            d['@context'] = AP_CONTEXT
        return d


class ArtistMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False)
    name = serializers.CharField()


class ReleaseMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False)
    title = serializers.CharField()


class RecordingMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False)
    title = serializers.CharField()


class AudioMetadataSerializer(serializers.Serializer):
    artist = ArtistMetadataSerializer()
    release = ReleaseMetadataSerializer()
    recording = RecordingMetadataSerializer()


class AudioSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.URLField()
    url = serializers.JSONField()
    published = serializers.DateTimeField()
    updated = serializers.DateTimeField(required=False)
    metadata = AudioMetadataSerializer()

    def validate_type(self, v):
        if v != 'Audio':
            raise serializers.ValidationError('Invalid type for audio')
        return v

    def validate_url(self, v):
        try:
            url = v['href']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing href')

        try:
            media_type = v['mediaType']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing mediaType')

        if not media_type.startswith('audio/'):
            raise serializers.ValidationError('Invalid mediaType')

        return url

    def validate_url(self, v):
        try:
            url = v['href']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing href')

        try:
            media_type = v['mediaType']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing mediaType')

        if not media_type.startswith('audio/'):
            raise serializers.ValidationError('Invalid mediaType')

        return v

    def create(self, validated_data):
        defaults = {
            'audio_mimetype': validated_data['url']['mediaType'],
            'audio_url': validated_data['url']['href'],
            'metadata': validated_data['metadata'],
            'artist_name': validated_data['metadata']['artist']['name'],
            'album_title': validated_data['metadata']['release']['title'],
            'title': validated_data['metadata']['recording']['title'],
            'published_date': validated_data['published'],
            'modification_date': validated_data.get('updated'),
        }
        return models.LibraryTrack.objects.get_or_create(
            library=self.context['library'],
            url=validated_data['id'],
            defaults=defaults
        )[0]

    def to_representation(self, instance):
        track = instance.track
        album = instance.track.album
        artist = instance.track.artist

        d = {
            'type': 'Audio',
            'id': instance.get_federation_url(),
            'name': instance.track.full_name,
            'published': instance.creation_date.isoformat(),
            'updated': instance.modification_date.isoformat(),
            'metadata': {
                'artist': {
                    'musicbrainz_id': str(artist.mbid) if artist.mbid else None,
                    'name': artist.name,
                },
                'release': {
                    'musicbrainz_id': str(album.mbid) if album.mbid else None,
                    'title': album.title,
                },
                'recording': {
                    'musicbrainz_id': str(track.mbid) if track.mbid else None,
                    'title': track.title,
                },
            },
            'url': {
                'href': utils.full_url(instance.path),
                'type': 'Link',
                'mediaType': instance.mimetype
            },
            'attributedTo': [
                self.context['actor'].url
            ]
        }
        if self.context.get('include_ap_context', True):
            d['@context'] = AP_CONTEXT
        return d


class CollectionSerializer(serializers.Serializer):

    def to_representation(self, conf):
        d = {
            'id': conf['id'],
            'actor': conf['actor'].url,
            'totalItems': len(conf['items']),
            'type': 'Collection',
            'items': [
                conf['item_serializer'](
                    i,
                    context={
                        'actor': conf['actor'],
                        'include_ap_context': False}
                ).data
                for i in conf['items']
            ]
        }

        if self.context.get('include_ap_context', True):
            d['@context'] = AP_CONTEXT
        return d
