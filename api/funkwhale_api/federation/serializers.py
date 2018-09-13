import logging
import mimetypes
import urllib.parse

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers

from funkwhale_api.common import utils as funkwhale_utils
from funkwhale_api.music import models as music_models

from . import activity, models, utils

AP_CONTEXT = [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {},
]

logger = logging.getLogger(__name__)


class ActorSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500)
    outbox = serializers.URLField(max_length=500)
    inbox = serializers.URLField(max_length=500)
    type = serializers.ChoiceField(choices=models.TYPE_CHOICES)
    preferredUsername = serializers.CharField()
    manuallyApprovesFollowers = serializers.NullBooleanField(required=False)
    name = serializers.CharField(required=False, max_length=200)
    summary = serializers.CharField(max_length=None, required=False)
    followers = serializers.URLField(max_length=500, required=False, allow_null=True)
    following = serializers.URLField(max_length=500, required=False, allow_null=True)
    publicKey = serializers.JSONField(required=False)

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
                    "mediaType": mimetypes.guess_type(instance.user.avatar.path)[0],
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
        kwargs["domain"] = domain
        for endpoint, url in self.initial_data.get("endpoints", {}).items():
            if endpoint == "sharedInbox":
                kwargs["shared_inbox_url"] = url
                break
        try:
            kwargs["public_key"] = self.initial_data["publicKey"]["publicKeyPem"]
        except KeyError:
            pass
        return kwargs

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

        matching = models.Actor.objects.filter(fid__in=to + cc)
        if self.context.get("local_recipients", False):
            matching = matching.local()

        if not len(matching):
            raise serializers.ValidationError("No matching recipients found")

        actors_by_fid = {a.fid: a for a in matching}

        def match(recipients, actors):
            for r in recipients:
                if r == activity.PUBLIC_ADDRESS:
                    yield r
                else:
                    try:
                        yield actors[r]
                    except KeyError:
                        pass

        return {
            "to": list(match(to, actors_by_fid)),
            "cc": list(match(cc, actors_by_fid)),
        }


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
        return follow_class.objects.update_or_create(
            actor=self.validated_data["actor"],
            target=self.validated_data["object"],
            defaults=defaults,
        )[0]

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
            follow.target.schedule_scan()
        return follow


class UndoFollowSerializer(serializers.Serializer):
    id = serializers.URLField(max_length=500)
    actor = serializers.URLField(max_length=500)
    object = FollowSerializer()
    type = serializers.ChoiceField(choices=["Undo"])

    def validate_actor(self, v):
        expected = self.context.get("follow_target")
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
        try:
            validated_data["follow"] = models.Follow.objects.filter(
                actor=validated_data["actor"], target=validated_data["object"]["object"]
            ).get()
        except models.Follow.DoesNotExist:
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
    object = serializers.JSONField()

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


class PaginatedCollectionSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["Collection"])
    totalItems = serializers.IntegerField(min_value=0)
    actor = serializers.URLField(max_length=500)
    id = serializers.URLField(max_length=500)
    first = serializers.URLField(max_length=500)
    last = serializers.URLField(max_length=500)

    def to_representation(self, conf):
        paginator = Paginator(conf["items"], conf.get("page_size", 20))
        first = funkwhale_utils.set_query_parameter(conf["id"], page=1)
        current = first
        last = funkwhale_utils.set_query_parameter(conf["id"], page=paginator.num_pages)
        d = {
            "id": conf["id"],
            "actor": conf["actor"].fid,
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
    type = serializers.ChoiceField(choices=["Library"])
    name = serializers.CharField()
    summary = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    audience = serializers.ChoiceField(
        choices=["", None, "https://www.w3.org/ns/activitystreams#Public"],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def to_representation(self, library):
        conf = {
            "id": library.fid,
            "name": library.name,
            "summary": library.description,
            "page_size": 100,
            "actor": library.actor,
            "items": library.files.filter(import_status="finished"),
            "type": "Library",
        }
        r = super().to_representation(conf)
        r["audience"] = (
            "https://www.w3.org/ns/activitystreams#Public"
            if library.privacy_level == "public"
            else ""
        )
        return r

    def create(self, validated_data):
        actor = utils.retrieve(
            validated_data["actor"],
            queryset=models.Actor,
            serializer_class=ActorSerializer,
        )
        library, created = music_models.Library.objects.update_or_create(
            fid=validated_data["id"],
            actor=actor,
            defaults={
                "files_count": validated_data["totalItems"],
                "name": validated_data["name"],
                "description": validated_data["summary"],
                "privacy_level": "everyone"
                if validated_data["audience"]
                == "https://www.w3.org/ns/activitystreams#Public"
                else "me",
            },
        )
        return library


class CollectionPageSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["CollectionPage"])
    totalItems = serializers.IntegerField(min_value=0)
    items = serializers.ListField()
    actor = serializers.URLField(max_length=500)
    id = serializers.URLField(max_length=500)
    first = serializers.URLField(max_length=500)
    last = serializers.URLField(max_length=500)
    next = serializers.URLField(max_length=500, required=False)
    prev = serializers.URLField(max_length=500, required=False)
    partOf = serializers.URLField(max_length=500)

    def validate_items(self, v):
        item_serializer = self.context.get("item_serializer")
        if not item_serializer:
            return v
        raw_items = [item_serializer(data=i, context=self.context) for i in v]
        valid_items = []
        for i in raw_items:
            if i.is_valid():
                valid_items.append(i)
            else:
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
            "actor": conf["actor"].fid,
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


class ArtistMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField()


class ReleaseMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField()


class RecordingMetadataSerializer(serializers.Serializer):
    musicbrainz_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField()


class AudioMetadataSerializer(serializers.Serializer):
    artist = ArtistMetadataSerializer()
    release = ReleaseMetadataSerializer()
    recording = RecordingMetadataSerializer()
    bitrate = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    size = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    length = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class AudioSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.URLField(max_length=500)
    library = serializers.URLField(max_length=500)
    url = serializers.JSONField()
    published = serializers.DateTimeField()
    updated = serializers.DateTimeField(required=False)
    metadata = AudioMetadataSerializer()

    def validate_type(self, v):
        if v != "Audio":
            raise serializers.ValidationError("Invalid type for audio")
        return v

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
        try:
            return music_models.Library.objects.get(fid=v)
        except music_models.Library.DoesNotExist:
            raise serializers.ValidationError("Invalid library")

    def create(self, validated_data):
        defaults = {
            "mimetype": validated_data["url"]["mediaType"],
            "source": validated_data["url"]["href"],
            "creation_date": validated_data["published"],
            "modification_date": validated_data.get("updated"),
            "metadata": self.initial_data,
        }
        tf, created = validated_data["library"].files.update_or_create(
            fid=validated_data["id"], defaults=defaults
        )
        return tf

    def to_representation(self, instance):
        track = instance.track
        album = instance.track.album
        artist = instance.track.artist
        d = {
            "type": "Audio",
            "id": instance.get_federation_id(),
            "library": instance.library.get_federation_id(),
            "name": instance.track.full_name,
            "published": instance.creation_date.isoformat(),
            "metadata": {
                "artist": {
                    "musicbrainz_id": str(artist.mbid) if artist.mbid else None,
                    "name": artist.name,
                },
                "release": {
                    "musicbrainz_id": str(album.mbid) if album.mbid else None,
                    "title": album.title,
                },
                "recording": {
                    "musicbrainz_id": str(track.mbid) if track.mbid else None,
                    "title": track.title,
                },
                "bitrate": instance.bitrate,
                "size": instance.size,
                "length": instance.duration,
            },
            "url": {
                "href": utils.full_url(instance.listen_url),
                "type": "Link",
                "mediaType": instance.mimetype,
            },
        }
        if instance.modification_date:
            d["updated"] = instance.modification_date.isoformat()

        if self.context.get("include_ap_context", True):
            d["@context"] = AP_CONTEXT
        return d


class CollectionSerializer(serializers.Serializer):
    def to_representation(self, conf):
        d = {
            "id": conf["id"],
            "actor": conf["actor"].fid,
            "totalItems": len(conf["items"]),
            "type": "Collection",
            "items": [
                conf["item_serializer"](
                    i, context={"actor": conf["actor"], "include_ap_context": False}
                ).data
                for i in conf["items"]
            ],
        }

        if self.context.get("include_ap_context", True):
            d["@context"] = AP_CONTEXT
        return d
