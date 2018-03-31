import urllib.parse

from django.urls import reverse
from django.conf import settings

from rest_framework import serializers
from dynamic_preferences.registries import global_preferences_registry

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
