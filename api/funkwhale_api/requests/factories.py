import factory

from funkwhale_api.factories import registry
from funkwhale_api.users.factories import UserFactory


@registry.register
class ImportRequestFactory(factory.django.DjangoModelFactory):
    artist_name = factory.Faker("name")
    albums = factory.Faker("sentence")
    user = factory.SubFactory(UserFactory)
    comment = factory.Faker("paragraph")

    class Meta:
        model = "requests.ImportRequest"
