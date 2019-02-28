import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate

from funkwhale_api.federation import factories as federation_factories


@registry.register
class MutationFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")
    created_by = factory.SubFactory(federation_factories.ActorFactory)
    summary = factory.Faker("paragraph")
    type = "update"

    class Meta:
        model = "common.Mutation"

    @factory.post_generation
    def target(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        self.target = extracted
        self.save()
