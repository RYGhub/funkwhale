import datetime

import pytest

from funkwhale_api.audio import tasks


def test_fetch_rss_feeds(factories, settings, now, mocker):
    settings.PODCASTS_RSS_FEED_REFRESH_DELAY = 5
    prunable_date = now - datetime.timedelta(
        seconds=settings.PODCASTS_RSS_FEED_REFRESH_DELAY
    )
    fetch_rss_feed = mocker.patch.object(tasks.fetch_rss_feed, "delay")
    channels = [
        # recent, not fetched
        factories["audio.Channel"](actor__last_fetch_date=now, external=True),
        # old but not external, not fetched
        factories["audio.Channel"](actor__last_fetch_date=prunable_date),
        # old and external, fetched !
        factories["audio.Channel"](actor__last_fetch_date=prunable_date, external=True),
        factories["audio.Channel"](actor__last_fetch_date=prunable_date, external=True),
    ]

    tasks.fetch_rss_feeds()

    assert fetch_rss_feed.call_count == 2
    fetch_rss_feed.assert_any_call(rss_url=channels[2].rss_url)
    fetch_rss_feed.assert_any_call(rss_url=channels[3].rss_url)


def test_fetch_rss_feed(factories, mocker):
    channel = factories["audio.Channel"](external=True)

    get_channel_from_rss_url = mocker.patch.object(
        tasks.serializers, "get_channel_from_rss_url"
    )
    tasks.fetch_rss_feed(channel.rss_url)

    get_channel_from_rss_url.assert_called_once_with(channel.rss_url)


def test_fetch_rss_feed_blocked_is_deleted(factories, mocker):
    channel = factories["audio.Channel"](external=True)

    mocker.patch.object(
        tasks.serializers,
        "get_channel_from_rss_url",
        side_effect=tasks.serializers.BlockedFeedException(),
    )
    tasks.fetch_rss_feed(channel.rss_url)

    with pytest.raises(channel.DoesNotExist):
        channel.refresh_from_db()
