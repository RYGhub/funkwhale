import pytest

from django.urls import reverse

from funkwhale_api.audio import serializers


def test_channel_create(logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()

    data = {
        # TODO: cover
        "name": "My channel",
        "username": "mychannel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
    }

    url = reverse("api:v1:channels-list")
    response = logged_in_api_client.post(url, data, format="json")

    assert response.status_code == 201

    channel = actor.owned_channels.select_related("artist__description").latest("id")
    expected = serializers.ChannelSerializer(channel).data

    assert response.data == expected
    assert channel.artist.name == data["name"]
    assert channel.artist.attributed_to == actor
    assert (
        sorted(channel.artist.tagged_items.values_list("tag__name", flat=True))
        == data["tags"]
    )
    assert channel.attributed_to == actor
    assert channel.actor.summary == channel.artist.description.rendered
    assert channel.actor.preferred_username == data["username"]
    assert channel.library.privacy_level == "everyone"
    assert channel.library.actor == actor


def test_channel_detail(factories, logged_in_api_client):
    channel = factories["audio.Channel"](artist__description=None)
    url = reverse("api:v1:channels-detail", kwargs={"uuid": channel.uuid})
    expected = serializers.ChannelSerializer(
        channel, context={"subscriptions_count": True}
    ).data
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_channel_list(factories, logged_in_api_client):
    channel = factories["audio.Channel"](artist__description=None)
    url = reverse("api:v1:channels-list")
    expected = serializers.ChannelSerializer(channel).data
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "results": [expected],
        "count": 1,
        "next": None,
        "previous": None,
    }


def test_channel_update(logged_in_api_client, factories):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"](attributed_to=actor)

    data = {
        # TODO: cover
        "name": "new name"
    }

    url = reverse("api:v1:channels-detail", kwargs={"uuid": channel.uuid})
    response = logged_in_api_client.patch(url, data)

    assert response.status_code == 200

    channel.refresh_from_db()

    assert channel.artist.name == data["name"]


def test_channel_update_permission(logged_in_api_client, factories):
    logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"]()

    data = {"name": "new name"}

    url = reverse("api:v1:channels-detail", kwargs={"uuid": channel.uuid})
    response = logged_in_api_client.patch(url, data)

    assert response.status_code == 403


def test_channel_delete(logged_in_api_client, factories):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"](attributed_to=actor)

    url = reverse("api:v1:channels-detail", kwargs={"uuid": channel.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204

    with pytest.raises(channel.DoesNotExist):
        channel.refresh_from_db()


def test_channel_delete_permission(logged_in_api_client, factories):
    logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"]()

    url = reverse("api:v1:channels-detail", kwargs={"uuid": channel.uuid})
    response = logged_in_api_client.patch(url)

    assert response.status_code == 403
    channel.refresh_from_db()


@pytest.mark.parametrize("url_name", ["api:v1:channels-list"])
def test_channel_views_disabled_via_feature_flag(
    url_name, logged_in_api_client, preferences
):
    preferences["audio__channels_enabled"] = False
    url = reverse(url_name)
    response = logged_in_api_client.get(url)
    assert response.status_code == 405


def test_channel_subscribe(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"](artist__description=None)
    url = reverse("api:v1:channels-subscribe", kwargs={"uuid": channel.uuid})

    response = logged_in_api_client.post(url)

    assert response.status_code == 201

    subscription = actor.emitted_follows.select_related(
        "target__channel__artist__description"
    ).latest("id")
    assert subscription.fid == subscription.get_federation_id()
    expected = serializers.SubscriptionSerializer(subscription).data
    assert response.data == expected
    assert subscription.target == channel.actor


def test_channel_unsubscribe(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"]()
    subscription = factories["audio.Subscription"](target=channel.actor, actor=actor)
    url = reverse("api:v1:channels-unsubscribe", kwargs={"uuid": channel.uuid})

    response = logged_in_api_client.post(url)

    assert response.status_code == 204

    with pytest.raises(subscription.DoesNotExist):
        subscription.refresh_from_db()


def test_subscriptions_list(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"](artist__description=None)
    subscription = factories["audio.Subscription"](target=channel.actor, actor=actor)
    factories["audio.Subscription"](target=channel.actor)
    url = reverse("api:v1:subscriptions-list")
    expected = serializers.SubscriptionSerializer(subscription).data
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"][0] == expected
    assert response.data == {
        "results": [expected],
        "count": 1,
        "next": None,
        "previous": None,
    }


def test_subscriptions_all(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    channel = factories["audio.Channel"](artist__description=None)
    subscription = factories["audio.Subscription"](target=channel.actor, actor=actor)
    factories["audio.Subscription"](target=channel.actor)
    url = reverse("api:v1:subscriptions-all")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {"results": [subscription.uuid], "count": 1}
