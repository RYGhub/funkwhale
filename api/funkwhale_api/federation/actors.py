import datetime
import logging
import uuid
import xml

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from rest_framework.exceptions import PermissionDenied

from dynamic_preferences.registries import global_preferences_registry

from funkwhale_api.common import preferences
from funkwhale_api.common import session
from funkwhale_api.common import utils as funkwhale_utils
from funkwhale_api.music import models as music_models
from funkwhale_api.music import tasks as music_tasks

from . import activity
from . import keys
from . import models
from . import serializers
from . import signing
from . import utils

logger = logging.getLogger(__name__)


def remove_tags(text):
    logger.debug("Removing tags from %s", text)
    return "".join(
        xml.etree.ElementTree.fromstring("<div>{}</div>".format(text)).itertext()
    )


def get_actor_data(actor_url):
    response = session.get_session().get(
        actor_url,
        timeout=5,
        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
        headers={"Accept": "application/activity+json"},
    )
    response.raise_for_status()
    try:
        return response.json()
    except:
        raise ValueError("Invalid actor payload: {}".format(response.text))


def get_actor(actor_url):
    try:
        actor = models.Actor.objects.get(url=actor_url)
    except models.Actor.DoesNotExist:
        actor = None
    fetch_delta = datetime.timedelta(
        minutes=preferences.get("federation__actor_fetch_delay")
    )
    if actor and actor.last_fetch_date > timezone.now() - fetch_delta:
        # cache is hot, we can return as is
        return actor
    data = get_actor_data(actor_url)
    serializer = serializers.ActorSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    return serializer.save(last_fetch_date=timezone.now())


class SystemActor(object):
    additional_attributes = {}
    manually_approves_followers = False

    def get_request_auth(self):
        actor = self.get_actor_instance()
        return signing.get_auth(actor.private_key, actor.private_key_id)

    def serialize(self):
        actor = self.get_actor_instance()
        serializer = serializers.ActorSerializer(actor)
        return serializer.data

    def get_actor_instance(self):
        try:
            return models.Actor.objects.get(url=self.get_actor_url())
        except models.Actor.DoesNotExist:
            pass
        private, public = keys.get_key_pair()
        args = self.get_instance_argument(
            self.id, name=self.name, summary=self.summary, **self.additional_attributes
        )
        args["private_key"] = private.decode("utf-8")
        args["public_key"] = public.decode("utf-8")
        return models.Actor.objects.create(**args)

    def get_actor_url(self):
        return utils.full_url(
            reverse("federation:instance-actors-detail", kwargs={"actor": self.id})
        )

    def get_instance_argument(self, id, name, summary, **kwargs):
        p = {
            "preferred_username": id,
            "domain": settings.FEDERATION_HOSTNAME,
            "type": "Person",
            "name": name.format(host=settings.FEDERATION_HOSTNAME),
            "manually_approves_followers": True,
            "url": self.get_actor_url(),
            "shared_inbox_url": utils.full_url(
                reverse("federation:instance-actors-inbox", kwargs={"actor": id})
            ),
            "inbox_url": utils.full_url(
                reverse("federation:instance-actors-inbox", kwargs={"actor": id})
            ),
            "outbox_url": utils.full_url(
                reverse("federation:instance-actors-outbox", kwargs={"actor": id})
            ),
            "summary": summary.format(host=settings.FEDERATION_HOSTNAME),
        }
        p.update(kwargs)
        return p

    def get_inbox(self, data, actor=None):
        raise NotImplementedError

    def post_inbox(self, data, actor=None):
        return self.handle(data, actor=actor)

    def get_outbox(self, data, actor=None):
        raise NotImplementedError

    def post_outbox(self, data, actor=None):
        raise NotImplementedError

    def handle(self, data, actor=None):
        """
        Main entrypoint for handling activities posted to the
        actor's inbox
        """
        logger.info("Received activity on %s inbox", self.id)

        if actor is None:
            raise PermissionDenied("Actor not authenticated")

        serializer = serializers.ActivitySerializer(data=data, context={"actor": actor})
        serializer.is_valid(raise_exception=True)

        ac = serializer.data
        try:
            handler = getattr(self, "handle_{}".format(ac["type"].lower()))
        except (KeyError, AttributeError):
            logger.debug("No handler for activity %s", ac["type"])
            return

        return handler(data, actor)

    def handle_follow(self, ac, sender):
        system_actor = self.get_actor_instance()
        serializer = serializers.FollowSerializer(
            data=ac, context={"follow_actor": sender}
        )
        if not serializer.is_valid():
            return logger.info("Invalid follow payload")
        approved = True if not self.manually_approves_followers else None
        follow = serializer.save(approved=approved)
        if follow.approved:
            return activity.accept_follow(follow)

    def handle_accept(self, ac, sender):
        system_actor = self.get_actor_instance()
        serializer = serializers.AcceptFollowSerializer(
            data=ac, context={"follow_target": sender, "follow_actor": system_actor}
        )
        if not serializer.is_valid(raise_exception=True):
            return logger.info("Received invalid payload")

        return serializer.save()

    def handle_undo_follow(self, ac, sender):
        system_actor = self.get_actor_instance()
        serializer = serializers.UndoFollowSerializer(
            data=ac, context={"actor": sender, "target": system_actor}
        )
        if not serializer.is_valid():
            return logger.info("Received invalid payload")
        serializer.save()

    def handle_undo(self, ac, sender):
        if ac["object"]["type"] != "Follow":
            return

        if ac["object"]["actor"] != sender.url:
            # not the same actor, permission issue
            return

        self.handle_undo_follow(ac, sender)


class LibraryActor(SystemActor):
    id = "library"
    name = "{host}'s library"
    summary = "Bot account to federate with {host}'s library"
    additional_attributes = {"manually_approves_followers": True}

    def serialize(self):
        data = super().serialize()
        urls = data.setdefault("url", [])
        urls.append(
            {
                "type": "Link",
                "mediaType": "application/activity+json",
                "name": "library",
                "href": utils.full_url(reverse("federation:music:files-list")),
            }
        )
        return data

    @property
    def manually_approves_followers(self):
        return preferences.get("federation__music_needs_approval")

    @transaction.atomic
    def handle_create(self, ac, sender):
        try:
            remote_library = models.Library.objects.get(
                actor=sender, federation_enabled=True
            )
        except models.Library.DoesNotExist:
            logger.info("Skipping import, we're not following %s", sender.url)
            return

        if ac["object"]["type"] != "Collection":
            return

        if ac["object"]["totalItems"] <= 0:
            return

        try:
            items = ac["object"]["items"]
        except KeyError:
            logger.warning("No items in collection!")
            return

        item_serializers = [
            serializers.AudioSerializer(data=i, context={"library": remote_library})
            for i in items
        ]
        now = timezone.now()
        valid_serializers = []
        for s in item_serializers:
            if s.is_valid():
                valid_serializers.append(s)
            else:
                logger.debug("Skipping invalid item %s, %s", s.initial_data, s.errors)

        lts = []
        for s in valid_serializers:
            lts.append(s.save())

        if remote_library.autoimport:
            batch = music_models.ImportBatch.objects.create(source="federation")
            for lt in lts:
                if lt.creation_date < now:
                    # track was already in the library, we do not trigger
                    # an import
                    continue
                job = music_models.ImportJob.objects.create(
                    batch=batch, library_track=lt, mbid=lt.mbid, source=lt.url
                )
                funkwhale_utils.on_commit(
                    music_tasks.import_job_run.delay,
                    import_job_id=job.pk,
                    use_acoustid=False,
                )


class TestActor(SystemActor):
    id = "test"
    name = "{host}'s test account"
    summary = (
        "Bot account to test federation with {host}. "
        "Send me /ping and I'll answer you."
    )
    additional_attributes = {"manually_approves_followers": False}
    manually_approves_followers = False

    def get_outbox(self, data, actor=None):
        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
                {},
            ],
            "id": utils.full_url(
                reverse("federation:instance-actors-outbox", kwargs={"actor": self.id})
            ),
            "type": "OrderedCollection",
            "totalItems": 0,
            "orderedItems": [],
        }

    def parse_command(self, message):
        """
        Remove any links or fancy markup to extract /command from
        a note message.
        """
        raw = remove_tags(message)
        try:
            return raw.split("/")[1]
        except IndexError:
            return

    def handle_create(self, ac, sender):
        if ac["object"]["type"] != "Note":
            return

        # we received a toot \o/
        command = self.parse_command(ac["object"]["content"])
        logger.debug("Parsed command: %s", command)
        if command != "ping":
            return

        now = timezone.now()
        test_actor = self.get_actor_instance()
        reply_url = "https://{}/activities/note/{}".format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        )
        reply_content = "{} Pong!".format(sender.mention_username)
        reply_activity = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
                {},
            ],
            "type": "Create",
            "actor": test_actor.url,
            "id": "{}/activity".format(reply_url),
            "published": now.isoformat(),
            "to": ac["actor"],
            "cc": [],
            "object": {
                "type": "Note",
                "content": "Pong!",
                "summary": None,
                "published": now.isoformat(),
                "id": reply_url,
                "inReplyTo": ac["object"]["id"],
                "sensitive": False,
                "url": reply_url,
                "to": [ac["actor"]],
                "attributedTo": test_actor.url,
                "cc": [],
                "attachment": [],
                "tag": [
                    {
                        "type": "Mention",
                        "href": ac["actor"],
                        "name": sender.mention_username,
                    }
                ],
            },
        }
        activity.deliver(reply_activity, to=[ac["actor"]], on_behalf_of=test_actor)

    def handle_follow(self, ac, sender):
        super().handle_follow(ac, sender)
        # also, we follow back
        test_actor = self.get_actor_instance()
        follow_back = models.Follow.objects.get_or_create(
            actor=test_actor, target=sender, approved=None
        )[0]
        activity.deliver(
            serializers.FollowSerializer(follow_back).data,
            to=[follow_back.target.url],
            on_behalf_of=follow_back.actor,
        )

    def handle_undo_follow(self, ac, sender):
        super().handle_undo_follow(ac, sender)
        actor = self.get_actor_instance()
        # we also unfollow the sender, if possible
        try:
            follow = models.Follow.objects.get(target=sender, actor=actor)
        except models.Follow.DoesNotExist:
            return
        undo = serializers.UndoFollowSerializer(follow).data
        follow.delete()
        activity.deliver(undo, to=[sender.url], on_behalf_of=actor)


SYSTEM_ACTORS = {"library": LibraryActor(), "test": TestActor()}
