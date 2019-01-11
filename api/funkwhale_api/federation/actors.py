import datetime
import logging

from django.conf import settings
from django.utils import timezone

from funkwhale_api.common import preferences, session

from . import models, serializers

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
            actor = models.Actor.objects.get(fid=fid)
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
