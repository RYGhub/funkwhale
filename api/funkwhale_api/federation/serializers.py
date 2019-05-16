import logging
import mimetypes
import urllib.parse
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers

from funkwhale_api.common import utils as funkwhale_utils
from funkwhale_api.music import licenses
from funkwhale_api.music import models as music_models
from funkwhale_api.music import tasks as music_tasks

from . import activity, actors, contexts, jsonld, models, tasks, utils

AP_CONTEXT = jsonld.get_default_context()

logger = logging.getLogger(__name__)


class LinkSerializer(jsonld.JsonLdSerializer):
    type = serializers.ChoiceField(choices=[contexts.AS.Link])
    href = serializers.URLField(max_length=500)
    mediaType = serializers.CharField()

    class Meta:
        jsonld_mapping = {
            "href": jsonld.first_id(contexts.AS.href),
            "mediaType": jsonld.first_val(contexts.AS.mediaType),
        }

    def __init__(self, *args, **kwargs):
        self.allowed_mimetypes = kwargs.pop("allowed_mimetypes", [])
        super().__init__(*args, **kwargs)

    def validate_mediaType(self, v):
        if not self.allowed_mimetypes:
            # no restrictions
            return v
        for mt in self.allowed_mimetypes:
            if mt.endswith("/*"):
                if v.startswith(mt.replace("*", "")):
                    return v
            else:
                if v == mt:
                    return v
        raise serializers.ValidationError(
            "Invalid mimetype {}. Allowed: {}".format(v, self.allowed_mimetypes)
        )


class EndpointsSerializer(jsonld.JsonLdSerializer):
    sharedInbox = serializers.URLField(max_length=500, required=False)

    class Meta:
        jsonld_mapping = {"sharedInbox": jsonld.first_id(contexts.AS.sharedInbox)}


class PublicKeySerializer(jsonld.JsonLdSerializer):
    publicKeyPem = serializers.CharField(trim_whitespace=False)

    class Meta:
        jsonld_mapping = {"publicKeyPem": jsonld.first_val(contexts.SEC.publicKeyPem)}


class ActorSerializer(jsonld.JsonLdSerializer):
    id = serializers.URLField(max_length=500)
    outbox = serializers.URLField(max_length=500)
    inbox = serializers.URLField(max_length=500)
    type = serializers.ChoiceField(
        choices=[getattr(contexts.AS, c[0]) for c in models.TYPE_CHOICES]
    )
    preferredUsername = serializers.CharField()
    manuallyApprovesFollowers = serializers.NullBooleanField(required=False)
    name = serializers.CharField(required=False, max_length=200)
    summary = serializers.CharField(max_length=None, required=False)
    followers = serializers.URLField(max_length=500)
    following = serializers.URLField(max_length=500, required=False, allow_null=True)
    publicKey = PublicKeySerializer(required=False)
    endpoints = EndpointsSerializer(required=False)

    class Meta:
        jsonld_mapping = {
            "outbox": jsonld.first_id(contexts.AS.outbox),
            "inbox": jsonld.first_id(contexts.LDP.inbox),
            "following": jsonld.first_id(contexts.AS.following),
            "followers": jsonld.first_id(contexts.AS.followers),
            "preferredUsername": jsonld.first_val(contexts.AS.preferredUsername),
            "summary": jsonld.first_val(contexts.AS.summary),
            "name": jsonld.first_val(contexts.AS.name),
            "publicKey": jsonld.first_obj(contexts.SEC.publicKey),
            "manuallyApprovesFollowers": jsonld.first_val(
                contexts.AS.manuallyApprovesFollowers
            ),
            "mediaType": jsonld.first_val(contexts.AS.mediaType),
            "endpoints": jsonld.first_obj(contexts.AS.endpoints),
        }

    def to_representation(self, instance):
        ret = {
            "id": instance.fid,
            "outbox": instance.outbox_url,
            "inbox": instance.inbox_url,
            "preferredUsername": instance.preferred_username,
            "type": instance.type,
        }
        if instance.name:
            ret["name"] = instance.name
        if instance.followers_url:
            ret["followers"] = instance.followers_url
        if instance.following_url:
            ret["following"] = instance.following_url
        if instance.summary:
            ret["summary"] = instance.summary
        if instance.manually_approves_followers is not None:
            ret["manuallyApprovesFollowers"] = instance.manually_approves_followers

        ret["@context"] = AP_CONTEXT
        if instance.public_key:
            ret["publicKey"] = {
                "owner": instance.fid,
                "publicKeyPem": instance.public_key,
                "id": "{}#main-key".format(instance.fid),
            }
        ret["endpoints"] = {}
        if instance.shared_inbox_url:
            ret["endpoints"]["sharedInbox"] = instance.shared_inbox_url
        try:
            if instance.user.avatar:
                ret["icon"] = {
                    "type": "Image",
                    "mediaType": mimetypes.guess_type(instance.user.avatar_path)[0],
                    "url": utils.full_url(instance.user.avatar.crop["400x400"].url),
                }
        except ObjectDoesNotExist:
            pass
        return ret

    def prepare_missing_fields(self):
        kwargs = {
            "fid": self.validated_data["id"],
            "outbox_url": self.validated_data["outbox"],
            "inbox_url": self.validated_data["inbox"],
            "following_url": self.validated_data.get("following"),
            "followers_url": self.validated_data.get("followers"),
            "summary": self.validated_data.get("summary"),
            "type": self.validated_data["type"],
            "name": self.validated_data.get("name"),
            "preferred_username": self.validated_data["preferredUsername"],
        }
        maf = self.validated_data.get("manuallyApprovesFollowers")
        if maf is not None:
            kwargs["manually_approves_followers"] = maf
        domain = urllib.parse.urlparse(kwargs["fid"]).netloc
        domain, domain_created = models.Domain.objects.get_or_create(pk=domain)
        if domain_created and not domain.is_local:
            # first time we see the domain, we trigger nodeinfo fetching
            tasks.update_domain_nodeinfo(domain_name=domain.name)

        kwargs["domain"] = domain
        for endpoint, url in self.validated_data.get("endpoints", {}).items():
            if endpoint == "sharedInbox":
                kwargs["shared_inbox_url"] = url
                break
        try:
            kwargs["public_key"] = self.validated_data["publicKey"]["publicKeyPem"]
        except KeyError:
            pass
        return kwargs

    def validate_type(self, v):
        return v.split("#")[-1]

    def build(self):
        d = self.prepare_missing_fields()
        return models.Actor(**d)

    def save(self, **kwargs):
        d = self.prepare_missing_fields()
        d.update(kwargs)
        return models.Actor.objects.update_or_create(fid=d["fid"], defaults=d)[0]

    def validate_summary(self, value):
        if value:
            return value[:500]


class APIActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Actor
        fields = [
            "id",
            "fid",
            "url",
            "creation_date",
            "summary",
            "preferred_username",
            "name",
            "last_fetch_date",
            "domain",
            "type",
            "manually_approves_followers",
            "full_username",
        ]


class BaseActivitySerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500, required=False)
    type = serializers.CharField(max_length=100)
    actor = serializers.URLField(max_length=500)

    def validate_actor(self, v):
        expected = self.context.get("actor")
        if expected and expected.fid != v:
            raise serializers.ValidationError("Invalid actor")
        if expected:
            # avoid a DB lookup
            return expected
        try:
            return models.Actor.objects.get(fid=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Actor not found")

    def create(self, validated_data):
        return models.Activity.objects.create(
            fid=validated_data.get("id"),
            actor=validated_data["actor"],
            payload=self.initial_data,
            type=validated_data["type"],
        )

    def validate(self, data):
        data["recipients"] = self.validate_recipients(self.initial_data)
        return super().validate(data)

    def validate_recipients(self, payload):
        """
        Ensure we have at least a to/cc field with valid actors
        """
        to = payload.get("to", [])
        cc = payload.get("cc", [])

        if not to and not cc:
            raise serializers.ValidationError(
                "We cannot handle an activity with no recipient"
            )


class FollowSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500)
    object = serializers.URLField(max_length=500)
    actor = serializers.URLField(max_length=500)
    type = serializers.ChoiceField(choices=["Follow"])

    def validate_object(self, v):
        expected = self.context.get("follow_target")
        if self.parent:
            # it's probably an accept, so everything is inverted, the actor
            # the recipient does not matter
            recipient = None
        else:
            recipient = self.context.get("recipient")
        if expected and expected.fid != v:
            raise serializers.ValidationError("Invalid target")
        try:
            obj = models.Actor.objects.get(fid=v)
            if recipient and recipient.fid != obj.fid:
                raise serializers.ValidationError("Invalid target")
            return obj
        except models.Actor.DoesNotExist:
            pass
        try:
            qs = music_models.Library.objects.filter(fid=v)
            if recipient:
                qs = qs.filter(actor=recipient)
            return qs.get()
        except music_models.Library.DoesNotExist:
            pass

        raise serializers.ValidationError("Target not found")

    def validate_actor(self, v):
        expected = self.context.get("follow_actor")
        if expected and expected.fid != v:
            raise serializers.ValidationError("Invalid actor")
        try:
            return models.Actor.objects.get(fid=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Actor not found")

    def save(self, **kwargs):
        target = self.validated_data["object"]

        if target._meta.label == "music.Library":
            follow_class = models.LibraryFollow
        else:
            follow_class = models.Follow
        defaults = kwargs
        defaults["fid"] = self.validated_data["id"]
        approved = kwargs.pop("approved", None)
        follow, created = follow_class.objects.update_or_create(
            actor=self.validated_data["actor"],
            target=self.validated_data["object"],
            defaults=defaults,
        )
        if not created:
            # We likely received a new follow when we had an existing one in database
            # this can happen when two instances are out of sync, e.g because some
            # messages are not delivered properly. In this case, we don't change
            # the follow approved status and return the follow as is.
            # We set a new UUID to ensure the follow urls are updated properly
            # cf #830
            follow.uuid = uuid.uuid4()
            follow.save(update_fields=["uuid"])
            return follow

        # it's a brand new follow, we use the approved value stored earlier
        if approved != follow.approved:
            follow.approved = approved
            follow.save(update_fields=["approved"])

        return follow

    def to_representation(self, instance):
        return {
            "@context": AP_CONTEXT,
            "actor": instance.actor.fid,
            "id": instance.get_federation_id(),
            "object": instance.target.fid,
            "type": "Follow",
        }


class APIFollowSerializer(serializers.ModelSerializer):
    actor = APIActorSerializer()
    target = APIActorSerializer()

    class Meta:
        model = models.Follow
        fields = [
            "uuid",
            "id",
            "approved",
            "creation_date",
            "modification_date",
            "actor",
            "target",
        ]


class AcceptFollowSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500, required=False)
    actor = serializers.URLField(max_length=500)
    object = FollowSerializer()
    type = serializers.ChoiceField(choices=["Accept"])

    def validate_actor(self, v):
        expected = self.context.get("actor")
        if expected and expected.fid != v:
            raise serializers.ValidationError("Invalid actor")
        try:
            return models.Actor.objects.get(fid=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Actor not found")

    def validate(self, validated_data):
        # we ensure the accept actor actually match the follow target / library owner
        target = validated_data["object"]["object"]

        if target._meta.label == "music.Library":
            expected = target.actor
            follow_class = models.LibraryFollow
        else:
            expected = target
            follow_class = models.Follow
        if validated_data["actor"] != expected:
            raise serializers.ValidationError("Actor mismatch")
        try:
            validated_data["follow"] = (
                follow_class.objects.filter(
                    target=target, actor=validated_data["object"]["actor"]
                )
                .exclude(approved=True)
                .select_related()
                .get()
            )
        except follow_class.DoesNotExist:
            raise serializers.ValidationError("No follow to accept")
        return validated_data

    def to_representation(self, instance):
        if instance.target._meta.label == "music.Library":
            actor = instance.target.actor
        else:
            actor = instance.target

        return {
            "@context": AP_CONTEXT,
            "id": instance.get_federation_id() + "/accept",
            "type": "Accept",
            "actor": actor.fid,
            "object": FollowSerializer(instance).data,
        }

    def save(self):
        follow = self.validated_data["follow"]
        follow.approved = True
        follow.save()
        if follow.target._meta.label == "music.Library":
            follow.target.schedule_scan(actor=follow.actor)
        return follow


class UndoFollowSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500)
    actor = serializers.URLField(max_length=500)
    object = FollowSerializer()
    type = serializers.ChoiceField(choices=["Undo"])

    def validate_actor(self, v):
        expected = self.context.get("actor")

        if expected and expected.fid != v:
            raise serializers.ValidationError("Invalid actor")
        try:
            return models.Actor.objects.get(fid=v)
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Actor not found")

    def validate(self, validated_data):
        # we ensure the accept actor actually match the follow actor
        if validated_data["actor"] != validated_data["object"]["actor"]:
            raise serializers.ValidationError("Actor mismatch")

        target = validated_data["object"]["object"]

        if target._meta.label == "music.Library":
            follow_class = models.LibraryFollow
        else:
            follow_class = models.Follow

        try:
            validated_data["follow"] = follow_class.objects.filter(
                actor=validated_data["actor"], target=target
            ).get()
        except follow_class.DoesNotExist:
            raise serializers.ValidationError("No follow to remove")
        return validated_data

    def to_representation(self, instance):
        return {
            "@context": AP_CONTEXT,
            "id": instance.get_federation_id() + "/undo",
            "type": "Undo",
            "actor": instance.actor.fid,
            "object": FollowSerializer(instance).data,
        }

    def save(self):
        return self.validated_data["follow"].delete()


class ActorWebfingerSerializer(serializers.Serializer):
    subject = serializers.CharField()
    aliases = serializers.ListField(child=serializers.URLField(max_length=500))
    links = serializers.ListField()
    actor_url = serializers.URLField(max_length=500, required=False)

    def validate(self, validated_data):
        validated_data["actor_url"] = None
        for l in validated_data["links"]:
            try:
                if not l["rel"] == "self":
                    continue
                if not l["type"] == "application/activity+json":
                    continue
                validated_data["actor_url"] = l["href"]
                break
            except KeyError:
                pass
        if validated_data["actor_url"] is None:
            raise serializers.ValidationError("No valid actor url found")
        return validated_data

    def to_representation(self, instance):
        data = {}
        data["subject"] = "acct:{}".format(instance.webfinger_subject)
        data["links"] = [
            {"rel": "self", "href": instance.fid, "type": "application/activity+json"}
        ]
        data["aliases"] = [instance.fid]
        return data


class ActivitySerializer(serializers.Serializer):
    actor = serializers.URLField(max_length=500)
    id = serializers.URLField(max_length=500, required=False)
    type = serializers.ChoiceField(choices=[(c, c) for c in activity.ACTIVITY_TYPES])
    object = serializers.JSONField(required=False)
    target = serializers.JSONField(required=False)

    def validate_object(self, value):
        try:
            type = value["type"]
        except KeyError:
            raise serializers.ValidationError("Missing object type")
        except TypeError:
            # probably a URL
            return value
        try:
            object_serializer = OBJECT_SERIALIZERS[type]
        except KeyError:
            raise serializers.ValidationError("Unsupported type {}".format(type))

        serializer = object_serializer(data=value)
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def validate_actor(self, value):
        request_actor = self.context.get("actor")
        if request_actor and request_actor.fid != value:
            raise serializers.ValidationError(
                "The actor making the request do not match" " the activity actor"
            )
        return value

    def to_representation(self, conf):
        d = {}
        d.update(conf)

        if self.context.get("include_ap_context", True):
            d["@context"] = AP_CONTEXT
        return d


class ObjectSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500)
    url = serializers.URLField(max_length=500, required=False, allow_null=True)
    type = serializers.ChoiceField(choices=[(c, c) for c in activity.OBJECT_TYPES])
    content = serializers.CharField(required=False, allow_null=True)
    summary = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    published = serializers.DateTimeField(required=False, allow_null=True)
    updated = serializers.DateTimeField(required=False, allow_null=True)
    to = serializers.ListField(
        child=serializers.URLField(max_length=500), required=False, allow_null=True
    )
    cc = serializers.ListField(
        child=serializers.URLField(max_length=500), required=False, allow_null=True
    )
    bto = serializers.ListField(
        child=serializers.URLField(max_length=500), required=False, allow_null=True
    )
    bcc = serializers.ListField(
        child=serializers.URLField(max_length=500), required=False, allow_null=True
    )


OBJECT_SERIALIZERS = {t: ObjectSerializer for t in activity.OBJECT_TYPES}


def get_additional_fields(data):
    UNSET = object()
    additional_fields = {}
    for field in ["name", "summary"]:
        v = data.get(field, UNSET)
        if v == UNSET:
            continue
        additional_fields[field] = v

    return additional_fields


PAGINATED_COLLECTION_JSONLD_MAPPING = {
    "totalItems": jsonld.first_val(contexts.AS.totalItems),
    "actor": jsonld.first_id(contexts.AS.actor),
    "attributedTo": jsonld.first_id(contexts.AS.attributedTo),
    "first": jsonld.first_id(contexts.AS.first),
    "last": jsonld.first_id(contexts.AS.last),
    "partOf": jsonld.first_id(contexts.AS.partOf),
}


class PaginatedCollectionSerializer(jsonld.JsonLdSerializer):
    type = serializers.ChoiceField(choices=[contexts.AS.Collection])
    totalItems = serializers.IntegerField(min_value=0)
    actor = serializers.URLField(max_length=500, required=False)
    attributedTo = serializers.URLField(max_length=500, required=False)
    id = serializers.URLField(max_length=500)
    first = serializers.URLField(max_length=500)
    last = serializers.URLField(max_length=500)

    class Meta:
        jsonld_mapping = PAGINATED_COLLECTION_JSONLD_MAPPING

    def validate(self, validated_data):
        d = super().validate(validated_data)
        actor = d.get("actor")
        attributed_to = d.get("attributedTo")
        if not actor and not attributed_to:
            raise serializers.ValidationError(
                "You need to provide at least actor or attributedTo"
            )

        d["attributedTo"] = attributed_to or actor
        return d

    def to_representation(self, conf):
        paginator = Paginator(conf["items"], conf.get("page_size", 20))
        first = funkwhale_utils.set_query_parameter(conf["id"], page=1)
        current = first
        last = funkwhale_utils.set_query_parameter(conf["id"], page=paginator.num_pages)
        d = {
            "id": conf["id"],
            # XXX Stable release: remove the obsolete actor field
            "actor": conf["actor"].fid,
            "attributedTo": conf["actor"].fid,
            "totalItems": paginator.count,
            "type": conf.get("type", "Collection"),
            "current": current,
            "first": first,
            "last": last,
        }
        d.update(get_additional_fields(conf))
        if self.context.get("include_ap_context", True):
            d["@context"] = AP_CONTEXT
        return d


class LibrarySerializer(PaginatedCollectionSerializer):
    type = serializers.ChoiceField(
        choices=[contexts.AS.Collection, contexts.FW.Library]
    )
    name = serializers.CharField()
    summary = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    followers = serializers.URLField(max_length=500)
    audience = serializers.ChoiceField(
        choices=["", "./", None, "https://www.w3.org/ns/activitystreams#Public"],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        jsonld_mapping = funkwhale_utils.concat_dicts(
            PAGINATED_COLLECTION_JSONLD_MAPPING,
            {
                "name": jsonld.first_val(contexts.AS.name),
                "summary": jsonld.first_val(contexts.AS.summary),
                "audience": jsonld.first_id(contexts.AS.audience),
                "followers": jsonld.first_id(contexts.AS.followers),
            },
        )

    def to_representation(self, library):
        conf = {
            "id": library.fid,
            "name": library.name,
            "summary": library.description,
            "page_size": 100,
            # XXX Stable release: remove the obsolete actor field
            "actor": library.actor,
            "attributedTo": library.actor,
            "items": library.uploads.for_federation(),
            "type": "Library",
        }
        r = super().to_representation(conf)
        r["audience"] = (
            contexts.AS.Public if library.privacy_level == "everyone" else ""
        )
        r["followers"] = library.followers_url
        return r

    def create(self, validated_data):
        actor = utils.retrieve_ap_object(
            validated_data["attributedTo"],
            actor=self.context.get("fetch_actor"),
            queryset=models.Actor,
            serializer_class=ActorSerializer,
        )
        privacy = {"": "me", "./": "me", None: "me", contexts.AS.Public: "everyone"}
        library, created = music_models.Library.objects.update_or_create(
            fid=validated_data["id"],
            actor=actor,
            defaults={
                "uploads_count": validated_data["totalItems"],
                "name": validated_data["name"],
                "description": validated_data.get("summary"),
                "followers_url": validated_data["followers"],
                "privacy_level": privacy[validated_data["audience"]],
            },
        )
        return library


class CollectionPageSerializer(jsonld.JsonLdSerializer):
    type = serializers.ChoiceField(choices=[contexts.AS.CollectionPage])
    totalItems = serializers.IntegerField(min_value=0)
    items = serializers.ListField()
    actor = serializers.URLField(max_length=500, required=False)
    attributedTo = serializers.URLField(max_length=500, required=False)
    id = serializers.URLField(max_length=500)
    first = serializers.URLField(max_length=500)
    last = serializers.URLField(max_length=500)
    next = serializers.URLField(max_length=500, required=False)
    prev = serializers.URLField(max_length=500, required=False)
    partOf = serializers.URLField(max_length=500)

    class Meta:
        jsonld_mapping = {
            "totalItems": jsonld.first_val(contexts.AS.totalItems),
            "items": jsonld.raw(contexts.AS.items),
            "actor": jsonld.first_id(contexts.AS.actor),
            "attributedTo": jsonld.first_id(contexts.AS.attributedTo),
            "first": jsonld.first_id(contexts.AS.first),
            "last": jsonld.first_id(contexts.AS.last),
            "next": jsonld.first_id(contexts.AS.next),
            "prev": jsonld.first_id(contexts.AS.prev),
            "partOf": jsonld.first_id(contexts.AS.partOf),
        }

    def validate_items(self, v):
        item_serializer = self.context.get("item_serializer")
        if not item_serializer:
            return v
        raw_items = [item_serializer(data=i, context=self.context) for i in v]
        valid_items = []
        for i in raw_items:
            try:
                i.is_valid(raise_exception=True)
                valid_items.append(i)
            except serializers.ValidationError:
                logger.debug("Invalid item %s: %s", i.data, i.errors)

        return valid_items

    def to_representation(self, conf):
        page = conf["page"]
        first = funkwhale_utils.set_query_parameter(conf["id"], page=1)
        last = funkwhale_utils.set_query_parameter(
            conf["id"], page=page.paginator.num_pages
        )
        id = funkwhale_utils.set_query_parameter(conf["id"], page=page.number)
        d = {
            "id": id,
            "partOf": conf["id"],
            # XXX Stable release: remove the obsolete actor field
            "actor": conf["actor"].fid,
            "attributedTo": conf["actor"].fid,
            "totalItems": page.paginator.count,
            "type": "CollectionPage",
            "first": first,
            "last": last,
            "items": [
                conf["item_serializer"](
                    i, context={"actor": conf["actor"], "include_ap_context": False}
                ).data
                for i in page.object_list
            ],
        }

        if page.has_previous():
            d["prev"] = funkwhale_utils.set_query_parameter(
                conf["id"], page=page.previous_page_number()
            )

        if page.has_next():
            d["next"] = funkwhale_utils.set_query_parameter(
                conf["id"], page=page.next_page_number()
            )
        d.update(get_additional_fields(conf))
        if self.context.get("include_ap_context", True):
            d["@context"] = AP_CONTEXT
        return d


MUSIC_ENTITY_JSONLD_MAPPING = {
    "name": jsonld.first_val(contexts.AS.name),
    "published": jsonld.first_val(contexts.AS.published),
    "musicbrainzId": jsonld.first_val(contexts.FW.musicbrainzId),
    "attributedTo": jsonld.first_id(contexts.AS.attributedTo),
}


class MusicEntitySerializer(jsonld.JsonLdSerializer):
    id = serializers.URLField(max_length=500)
    published = serializers.DateTimeField()
    musicbrainzId = serializers.UUIDField(allow_null=True, required=False)
    name = serializers.CharField(max_length=1000)
    attributedTo = serializers.URLField(max_length=500, allow_null=True, required=False)
    updateable_fields = []

    def update(self, instance, validated_data):
        attributed_to_fid = validated_data.get("attributedTo")
        if attributed_to_fid:
            validated_data["attributedTo"] = actors.get_actor(attributed_to_fid)
        updated_fields = funkwhale_utils.get_updated_fields(
            self.updateable_fields, validated_data, instance
        )
        if updated_fields:
            return music_tasks.update_library_entity(instance, updated_fields)

        return instance


class ArtistSerializer(MusicEntitySerializer):
    updateable_fields = [
        ("name", "name"),
        ("musicbrainzId", "mbid"),
        ("attributedTo", "attributed_to"),
    ]

    class Meta:
        model = music_models.Artist
        jsonld_mapping = MUSIC_ENTITY_JSONLD_MAPPING

    def to_representation(self, instance):
        d = {
            "type": "Artist",
            "id": instance.fid,
            "name": instance.name,
            "published": instance.creation_date.isoformat(),
            "musicbrainzId": str(instance.mbid) if instance.mbid else None,
            "attributedTo": instance.attributed_to.fid
            if instance.attributed_to
            else None,
        }

        if self.context.get("include_ap_context", self.parent is None):
            d["@context"] = AP_CONTEXT
        return d


class AlbumSerializer(MusicEntitySerializer):
    released = serializers.DateField(allow_null=True, required=False)
    artists = serializers.ListField(child=ArtistSerializer(), min_length=1)
    cover = LinkSerializer(
        allowed_mimetypes=["image/*"], allow_null=True, required=False
    )
    updateable_fields = [
        ("name", "title"),
        ("musicbrainzId", "mbid"),
        ("attributedTo", "attributed_to"),
        ("released", "release_date"),
    ]

    class Meta:
        model = music_models.Album
        jsonld_mapping = funkwhale_utils.concat_dicts(
            MUSIC_ENTITY_JSONLD_MAPPING,
            {
                "released": jsonld.first_val(contexts.FW.released),
                "artists": jsonld.first_attr(contexts.FW.artists, "@list"),
                "cover": jsonld.first_obj(contexts.FW.cover),
            },
        )

    def to_representation(self, instance):
        d = {
            "type": "Album",
            "id": instance.fid,
            "name": instance.title,
            "published": instance.creation_date.isoformat(),
            "musicbrainzId": str(instance.mbid) if instance.mbid else None,
            "released": instance.release_date.isoformat()
            if instance.release_date
            else None,
            "artists": [
                ArtistSerializer(
                    instance.artist, context={"include_ap_context": False}
                ).data
            ],
            "attributedTo": instance.attributed_to.fid
            if instance.attributed_to
            else None,
        }
        if instance.cover:
            d["cover"] = {
                "type": "Link",
                "href": utils.full_url(instance.cover.url),
                "mediaType": mimetypes.guess_type(instance.cover_path)[0]
                or "image/jpeg",
            }
        if self.context.get("include_ap_context", self.parent is None):
            d["@context"] = AP_CONTEXT
        return d


class TrackSerializer(MusicEntitySerializer):
    position = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    disc = serializers.IntegerField(min_value=1, allow_null=True, required=False)
    artists = serializers.ListField(child=ArtistSerializer(), min_length=1)
    album = AlbumSerializer()
    license = serializers.URLField(allow_null=True, required=False)
    copyright = serializers.CharField(allow_null=True, required=False)

    updateable_fields = [
        ("name", "title"),
        ("musicbrainzId", "mbid"),
        ("attributedTo", "attributed_to"),
        ("disc", "disc_number"),
        ("position", "position"),
        ("copyright", "copyright"),
        ("license", "license"),
    ]

    class Meta:
        model = music_models.Track
        jsonld_mapping = funkwhale_utils.concat_dicts(
            MUSIC_ENTITY_JSONLD_MAPPING,
            {
                "album": jsonld.first_obj(contexts.FW.album),
                "artists": jsonld.first_attr(contexts.FW.artists, "@list"),
                "copyright": jsonld.first_val(contexts.FW.copyright),
                "disc": jsonld.first_val(contexts.FW.disc),
                "license": jsonld.first_id(contexts.FW.license),
                "position": jsonld.first_val(contexts.FW.position),
            },
        )

    def to_representation(self, instance):
        d = {
            "type": "Track",
            "id": instance.fid,
            "name": instance.title,
            "published": instance.creation_date.isoformat(),
            "musicbrainzId": str(instance.mbid) if instance.mbid else None,
            "position": instance.position,
            "disc": instance.disc_number,
            "license": instance.local_license["identifiers"][0]
            if instance.local_license
            else None,
            "copyright": instance.copyright if instance.copyright else None,
            "artists": [
                ArtistSerializer(
                    instance.artist, context={"include_ap_context": False}
                ).data
            ],
            "album": AlbumSerializer(
                instance.album, context={"include_ap_context": False}
            ).data,
            "attributedTo": instance.attributed_to.fid
            if instance.attributed_to
            else None,
        }

        if self.context.get("include_ap_context", self.parent is None):
            d["@context"] = AP_CONTEXT
        return d

    def create(self, validated_data):
        from funkwhale_api.music import tasks as music_tasks

        references = {}
        actors_to_fetch = set()
        actors_to_fetch.add(
            funkwhale_utils.recursive_getattr(
                validated_data, "attributedTo", permissive=True
            )
        )
        actors_to_fetch.add(
            funkwhale_utils.recursive_getattr(
                validated_data, "album.attributedTo", permissive=True
            )
        )
        artists = (
            funkwhale_utils.recursive_getattr(
                validated_data, "artists", permissive=True
            )
            or []
        )
        album_artists = (
            funkwhale_utils.recursive_getattr(
                validated_data, "album.artists", permissive=True
            )
            or []
        )
        for artist in artists + album_artists:
            actors_to_fetch.add(artist.get("attributedTo"))

        for url in actors_to_fetch:
            if not url:
                continue
            references[url] = actors.get_actor(url)

        metadata = music_tasks.federation_audio_track_to_metadata(
            validated_data, references
        )

        from_activity = self.context.get("activity")
        if from_activity:
            metadata["from_activity_id"] = from_activity.pk
        track = music_tasks.get_track_from_import_metadata(metadata, update_cover=True)
        return track

    def update(self, obj, validated_data):
        if validated_data.get("license"):
            validated_data["license"] = licenses.match(validated_data["license"])
        return super().update(obj, validated_data)


class UploadSerializer(jsonld.JsonLdSerializer):
    type = serializers.ChoiceField(choices=[contexts.AS.Audio])
    id = serializers.URLField(max_length=500)
    library = serializers.URLField(max_length=500)
    url = LinkSerializer(allowed_mimetypes=["audio/*"])
    published = serializers.DateTimeField()
    updated = serializers.DateTimeField(required=False, allow_null=True)
    bitrate = serializers.IntegerField(min_value=0)
    size = serializers.IntegerField(min_value=0)
    duration = serializers.IntegerField(min_value=0)

    track = TrackSerializer(required=True)

    class Meta:
        model = music_models.Upload
        jsonld_mapping = {
            "track": jsonld.first_obj(contexts.FW.track),
            "library": jsonld.first_id(contexts.FW.library),
            "url": jsonld.first_obj(contexts.AS.url),
            "published": jsonld.first_val(contexts.AS.published),
            "updated": jsonld.first_val(contexts.AS.updated),
            "duration": jsonld.first_val(contexts.AS.duration),
            "bitrate": jsonld.first_val(contexts.FW.bitrate),
            "size": jsonld.first_val(contexts.FW.size),
        }

    def validate_url(self, v):
        try:
            v["href"]
        except (KeyError, TypeError):
            raise serializers.ValidationError("Missing href")

        try:
            media_type = v["mediaType"]
        except (KeyError, TypeError):
            raise serializers.ValidationError("Missing mediaType")

        if not media_type or not media_type.startswith("audio/"):
            raise serializers.ValidationError("Invalid mediaType")

        return v

    def validate_library(self, v):
        lb = self.context.get("library")
        if lb:
            if lb.fid != v:
                raise serializers.ValidationError("Invalid library")
            return lb

        actor = self.context.get("actor")
        kwargs = {}
        if actor:
            kwargs["actor"] = actor
        try:
            return music_models.Library.objects.get(fid=v, **kwargs)
        except music_models.Library.DoesNotExist:
            raise serializers.ValidationError("Invalid library")

    def create(self, validated_data):
        try:
            return music_models.Upload.objects.get(fid=validated_data["id"])
        except music_models.Upload.DoesNotExist:
            pass

        track = TrackSerializer(
            context={"activity": self.context.get("activity")}
        ).create(validated_data["track"])

        data = {
            "fid": validated_data["id"],
            "mimetype": validated_data["url"]["mediaType"],
            "source": validated_data["url"]["href"],
            "creation_date": validated_data["published"],
            "modification_date": validated_data.get("updated"),
            "track": track,
            "duration": validated_data["duration"],
            "size": validated_data["size"],
            "bitrate": validated_data["bitrate"],
            "library": validated_data["library"],
            "from_activity": self.context.get("activity"),
            "import_status": "finished",
        }
        return music_models.Upload.objects.create(**data)

    def to_representation(self, instance):
        track = instance.track
        d = {
            "type": "Audio",
            "id": instance.get_federation_id(),
            "library": instance.library.fid,
            "name": track.full_name,
            "published": instance.creation_date.isoformat(),
            "bitrate": instance.bitrate,
            "size": instance.size,
            "duration": instance.duration,
            "url": {
                "href": utils.full_url(instance.listen_url),
                "type": "Link",
                "mediaType": instance.mimetype,
            },
            "track": TrackSerializer(track, context={"include_ap_context": False}).data,
        }
        if instance.modification_date:
            d["updated"] = instance.modification_date.isoformat()

        if self.context.get("include_ap_context", self.parent is None):
            d["@context"] = AP_CONTEXT
        return d


class NodeInfoLinkSerializer(serializers.Serializer):
    href = serializers.URLField()
    rel = serializers.URLField()


class NodeInfoSerializer(serializers.Serializer):
    links = serializers.ListField(child=NodeInfoLinkSerializer(), min_length=1)
