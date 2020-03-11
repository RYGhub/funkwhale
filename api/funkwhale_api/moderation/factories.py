import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.music import factories as music_factories
from funkwhale_api.users import factories as users_factories

from . import serializers


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


@registry.register
class NoteFactory(NoUpdateOnCreate, factory.DjangoModelFactory):
    author = factory.SubFactory(federation_factories.ActorFactory)
    target = None
    summary = factory.Faker("paragraph")

    class Meta:
        model = "moderation.Note"


@registry.register
class ReportFactory(NoUpdateOnCreate, factory.DjangoModelFactory):
    submitter = factory.SubFactory(federation_factories.ActorFactory)
    target = factory.SubFactory(music_factories.ArtistFactory)
    summary = factory.Faker("paragraph")
    type = "other"

    class Meta:
        model = "moderation.Report"

    class Params:
        anonymous = factory.Trait(actor=None, submitter_email=factory.Faker("email"))
        local = factory.Trait(fid=None)
        assigned = factory.Trait(
            assigned_to=factory.SubFactory(federation_factories.ActorFactory)
        )

    @factory.post_generation
    def _set_target_owner(self, create, extracted, **kwargs):
        if not self.target:
            return

        self.target_owner = serializers.get_target_owner(self.target)
