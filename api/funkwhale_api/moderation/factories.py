import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.music import factories as music_factories
from funkwhale_api.users import factories as users_factories


@registry.register
class InstancePolicyFactory(NoUpdateOnCreate, factory.DjangoModelFactory):
    summary = factory.Faker("paragraph")
    actor = factory.SubFactory(federation_factories.ActorFactory)
    block_all = True
    is_active = True

    class Meta:
        model = "moderation.InstancePolicy"

    class Params:
        for_domain = factory.Trait(
            target_domain=factory.SubFactory(federation_factories.DomainFactory)
        )
        for_actor = factory.Trait(
            target_actor=factory.SubFactory(federation_factories.ActorFactory)
        )


@registry.register
class UserFilterFactory(NoUpdateOnCreate, factory.DjangoModelFactory):
    user = factory.SubFactory(users_factories.UserFactory)
    target_artist = None

    class Meta:
        model = "moderation.UserFilter"

    class Params:
        for_artist = factory.Trait(
            target_artist=factory.SubFactory(music_factories.ArtistFactory)
        )
