from funkwhale_api.common import channels
from funkwhale_api.activity import record

from . import serializers

record.registry.register_serializer(
    serializers.TrackFavoriteActivitySerializer)


@record.registry.register_consumer('favorites.TrackFavorite')
def broadcast_track_favorite_to_instance_timeline(data, obj):
    if obj.user.privacy_level not in ['instance', 'everyone']:
        return
    channels.group_send('instance_timeline', {
        'type': 'event',
        'data': data
    })
