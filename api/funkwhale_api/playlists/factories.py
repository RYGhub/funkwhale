import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.music.factories import TrackFactory
from funkwhale_api.users.factories import UserFactory


@registry.register
class PlaylistFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = "playlists.Playlist"


@registry.register
class PlaylistTrackFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    playlist = factory.SubFactory(PlaylistFactory)
    track = factory.SubFactory(TrackFactory)

    class Meta:
        model = "playlists.PlaylistTrack"
