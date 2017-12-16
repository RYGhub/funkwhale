import factory
from funkwhale_api.music.tests import factories

from funkwhale_api.users.tests.factories import UserFactory


class ListeningFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    track = factory.SubFactory(factories.TrackFactory)

    class Meta:
        model = 'history.Listening'
