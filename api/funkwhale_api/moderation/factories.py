import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.federation import factories as federation_factories


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
