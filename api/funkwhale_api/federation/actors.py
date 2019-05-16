import datetime
import logging

from django.conf import settings
from django.utils import timezone

from funkwhale_api.common import preferences, session
from funkwhale_api.users import models as users_models

from . import keys, models, serializers

logger = logging.getLogger(__name__)


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
    except Exception:
        raise ValueError("Invalid actor payload: {}".format(response.text))


def get_actor(fid, skip_cache=False):
    if not skip_cache:
        try:
            actor = models.Actor.objects.select_related().get(fid=fid)
        except models.Actor.DoesNotExist:
            actor = None
        fetch_delta = datetime.timedelta(
            minutes=preferences.get("federation__actor_fetch_delay")
        )
        if actor and actor.last_fetch_date > timezone.now() - fetch_delta:
            # cache is hot, we can return as is
            return actor
    data = get_actor_data(fid)
    serializer = serializers.ActorSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    return serializer.save(last_fetch_date=timezone.now())


def get_service_actor():
    name, domain = (
        settings.FEDERATION_SERVICE_ACTOR_USERNAME,
        settings.FEDERATION_HOSTNAME,
    )
    try:
        return models.Actor.objects.select_related().get(
            preferred_username=name, domain__name=domain
        )
    except models.Actor.DoesNotExist:
        pass

    args = users_models.get_actor_data(name)
    private, public = keys.get_key_pair()
    args["private_key"] = private.decode("utf-8")
    args["public_key"] = public.decode("utf-8")
    args["type"] = "Service"
    return models.Actor.objects.create(**args)
