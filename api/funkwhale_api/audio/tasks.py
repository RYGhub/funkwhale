import datetime
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from funkwhale_api.taskapp import celery

from . import models
from . import serializers

logger = logging.getLogger(__name__)


@celery.app.task(name="audio.fetch_rss_feeds")
def fetch_rss_feeds():
    limit = timezone.now() - datetime.timedelta(
        seconds=settings.PODCASTS_RSS_FEED_REFRESH_DELAY
    )
    candidates = (
        models.Channel.objects.external_rss()
        .filter(actor__last_fetch_date__lte=limit)
        .values_list("rss_url", flat=True)
    )

    total = len(candidates)
    logger.info("Refreshing %s rss feeds…", total)
    for url in candidates:
        fetch_rss_feed.delay(rss_url=url)


@celery.app.task(name="audio.fetch_rss_feed")
@transaction.atomic
def fetch_rss_feed(rss_url):
    channel = (
        models.Channel.objects.external_rss()
        .filter(rss_url=rss_url)
        .order_by("id")
        .first()
    )
    if not channel:
        logger.warn("Cannot refresh non external feed")
        return

    try:
        serializers.get_channel_from_rss_url(rss_url)
    except serializers.BlockedFeedException:
        # channel was blocked since last fetch, let's delete it
        logger.info("Deleting blocked channel linked to %s", rss_url)
        channel.delete()
