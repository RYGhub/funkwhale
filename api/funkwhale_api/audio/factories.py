import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.music import factories as music_factories

from . import models


def set_actor(o):
    return models.generate_actor(str(o.uuid))


@registry.register
class ChannelFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    uuid = factory.Faker("uuid4")
    attributed_to = factory.SubFactory(federation_factories.ActorFactory)
    library = factory.SubFactory(
        federation_factories.MusicLibraryFactory,
        actor=factory.SelfAttribute("..attributed_to"),
        privacy_level="everyone",
    )
    actor = factory.LazyAttribute(set_actor)
    artist = factory.SubFactory(music_factories.ArtistFactory)

    class Meta:
        model = "audio.Channel"

    class Params:
        local = factory.Trait(
            attributed_to=factory.SubFactory(
                federation_factories.ActorFactory, local=True
            ),
            artist__local=True,
        )
