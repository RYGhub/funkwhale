import pytest

from django.urls import reverse

from funkwhale_api.federation import utils as federation_utils


def test_channel(factories, now):
    channel = factories["audio.Channel"]()
    assert channel.artist is not None
    assert channel.actor is not None
    assert channel.attributed_to is not None
    assert channel.library is not None
    assert channel.creation_date >= now


def test_channel_get_rss_url_local(factories):
    channel = factories["audio.Channel"](artist__local=True)
    expected = federation_utils.full_url(
        reverse(
            "api:v1:channels-rss",
            kwargs={"composite": channel.actor.preferred_username},
        )
    )
    assert channel.get_rss_url() == expected


def test_channel_get_rss_url_remote(factories):
    channel = factories["audio.Channel"]()
    assert channel.get_rss_url() == channel.rss_url


def test_channel_delete(factories):
    channel = factories["audio.Channel"]()
    library = channel.library
    actor = channel.library
    artist = channel.artist
    channel.delete()

    for obj in [library, actor, artist]:
        with pytest.raises(obj.DoesNotExist):
            obj.refresh_from_db()
