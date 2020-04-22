import pytest

from funkwhale_api.audio import filters
from funkwhale_api.audio import models


def test_channel_filter_subscribed_true(factories, mocker, queryset_equal_list):
    user = factories["users.User"](with_actor=True)
    channel = factories["audio.Channel"]()
    other_channel = factories["audio.Channel"]()
    factories["audio.Subscription"](target=channel.actor, actor=user.actor)
    factories["audio.Subscription"](target=other_channel.actor)

    qs = models.Channel.objects.all()
    filterset = filters.ChannelFilter(
        {"subscribed": "true"}, request=mocker.Mock(user=user), queryset=qs
    )

    assert filterset.qs == [channel]


def test_channel_filter_subscribed_false(factories, mocker, queryset_equal_list):
    user = factories["users.User"](with_actor=True)
    channel = factories["audio.Channel"]()
    other_channel = factories["audio.Channel"]()
    factories["audio.Subscription"](target=channel.actor, actor=user.actor)
    factories["audio.Subscription"](target=other_channel.actor)

    qs = models.Channel.objects.all()
    filterset = filters.ChannelFilter(
        {"subscribed": "false"}, request=mocker.Mock(user=user), queryset=qs
    )

    assert filterset.qs == [other_channel]


@pytest.mark.parametrize("external, expected_index", [("true", 0), ("false", 1)])
def test_channel_filter_external(
    external, expected_index, factories, mocker, queryset_equal_list
):
    user = factories["users.User"](with_actor=True)
    channels = [factories["audio.Channel"](external=True), factories["audio.Channel"]()]
    qs = models.Channel.objects.all()
    filterset = filters.ChannelFilter(
        {"external": external}, request=mocker.Mock(user=user), queryset=qs
    )

    assert filterset.qs == [channels[expected_index]]
