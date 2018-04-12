import json
import logging

from django.conf import settings
from django.utils import timezone

from requests.exceptions import RequestException

from funkwhale_api.common import session
from funkwhale_api.taskapp import celery

from . import actors
from . import library as lb
from . import models
from . import signing


logger = logging.getLogger(__name__)


@celery.app.task(
    name='federation.send',
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5)
@celery.require_instance(models.Actor, 'actor')
def send(activity, actor, to):
    logger.info('Preparing activity delivery to %s', to)
    auth = signing.get_auth(
        actor.private_key, actor.private_key_id)
    for url in to:
        recipient_actor = actors.get_actor(url)
        logger.debug('delivering to %s', recipient_actor.inbox_url)
        logger.debug('activity content: %s', json.dumps(activity))
        response = session.get_session().post(
            auth=auth,
            json=activity,
            url=recipient_actor.inbox_url,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={
                'Content-Type': 'application/activity+json'
            }
        )
        response.raise_for_status()
        logger.debug('Remote answered with %s', response.status_code)


@celery.app.task(
    name='federation.scan_library',
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5)
@celery.require_instance(models.Library, 'library')
def scan_library(library, until=None):
    if not library.federation_enabled:
        return

    data = lb.get_library_data(library.url)
    scan_library_page.delay(
        library_id=library.id, page_url=data['first'], until=until)
    library.fetched_date = timezone.now()
    library.tracks_count = data['totalItems']
    library.save(update_fields=['fetched_date', 'tracks_count'])


@celery.app.task(
    name='federation.scan_library_page',
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5)
@celery.require_instance(models.Library, 'library')
def scan_library_page(library, page_url, until=None):
    if not library.federation_enabled:
        return

    data = lb.get_library_page(library, page_url)
    lts = []
    for item_serializer in data['items']:
        item_date = item_serializer.validated_data['published']
        if until and item_date < until:
            return
        lts.append(item_serializer.save())

    next_page = data.get('next')
    if next_page and next_page != page_url:
        scan_library_page.delay(library_id=library.id, page_url=next_page)
