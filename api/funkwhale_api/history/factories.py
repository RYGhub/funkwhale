import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.music import factories
from funkwhale_api.users.factories import UserFactory


@registry.register
class ListeningFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    track = factory.SubFactory(factories.TrackFactory)

    class Meta:
        model = "history.Listening"
