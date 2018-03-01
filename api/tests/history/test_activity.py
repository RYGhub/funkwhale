from funkwhale_api.users.serializers import UserActivitySerializer
from funkwhale_api.music.serializers import TrackActivitySerializer
from funkwhale_api.history import serializers
from funkwhale_api.history import activities


def test_get_listening_activity_url(settings, factories):
    listening = factories['history.Listening']()
    user_url = listening.user.get_activity_url()
    expected = '{}/listenings/tracks/{}'.format(
        user_url, listening.pk)
    assert listening.get_activity_url() == expected


def test_activity_listening_serializer(factories):
    listening = factories['history.Listening']()

    actor = UserActivitySerializer(listening.user).data
    field = serializers.serializers.DateTimeField()
    expected = {
        "type": "Listen",
        "local_id": listening.pk,
        "id": listening.get_activity_url(),
        "actor": actor,
        "object": TrackActivitySerializer(listening.track).data,
        "published": field.to_representation(listening.end_date),
    }

    data = serializers.ListeningActivitySerializer(listening).data

    assert data == expected


def test_track_listening_serializer_is_connected(activity_registry):
    conf = activity_registry['history.Listening']
    assert conf['serializer'] == serializers.ListeningActivitySerializer


def test_track_listening_serializer_instance_activity_consumer(
        activity_registry):
    conf = activity_registry['history.Listening']
    consumer = activities.broadcast_listening_to_instance_activity
    assert consumer in conf['consumers']


def test_broadcast_listening_to_instance_activity(
        factories, mocker):
    p = mocker.patch('funkwhale_api.common.channels.group_send')
    listening = factories['history.Listening']()
    data = serializers.ListeningActivitySerializer(listening).data
    consumer = activities.broadcast_listening_to_instance_activity
    message = {
        "type": 'event.send',
        "text": '',
        "data": data
    }
    consumer(data=data, obj=listening)
    p.assert_called_once_with('instance_activity', message)


def test_broadcast_listening_to_instance_activity_private(
        factories, mocker):
    p = mocker.patch('funkwhale_api.common.channels.group_send')
    listening = factories['history.Listening'](
        user__privacy_level='me'
    )
    data = serializers.ListeningActivitySerializer(listening).data
    consumer = activities.broadcast_listening_to_instance_activity
    message = {
        "type": 'event.send',
        "text": '',
        "data": data
    }
    consumer(data=data, obj=listening)
    p.assert_not_called()
