import urllib.parse

from django.urls import reverse
from django.conf import settings

from rest_framework import serializers
from dynamic_preferences.registries import global_preferences_registry

from . import activity
from . import models
from . import utils


class ActorSerializer(serializers.ModelSerializer):
    # left maps to activitypub fields, right to our internal models
    id = serializers.URLField(source='url')
    outbox = serializers.URLField(source='outbox_url')
    inbox = serializers.URLField(source='inbox_url')
    following = serializers.URLField(source='following_url', required=False)
    followers = serializers.URLField(source='followers_url', required=False)
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
        ret['@context'] = [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ]
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


class ActorWebfingerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Actor
        fields = ['url']

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
