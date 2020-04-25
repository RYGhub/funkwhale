import uuid

import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate
from funkwhale_api.federation import actors
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.music import factories as music_factories

from . import models


def set_actor(o):
    return models.generate_actor(str(o.uuid))


def get_rss_channel_name():
    return "rssfeed-{}".format(uuid.uuid4())


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
    artist = factory.SubFactory(
        music_factories.ArtistFactory,
        attributed_to=factory.SelfAttribute("..attributed_to"),
    )
    rss_url = factory.Faker("url")
    metadata = factory.LazyAttribute(lambda o: {})

    class Meta:
        model = "audio.Channel"

    class Params:
        external = factory.Trait(
            attributed_to=factory.LazyFunction(actors.get_service_actor),
            library__privacy_level="me",
            actor=factory.SubFactory(
                federation_factories.ActorFactory,
                local=True,
                preferred_username=factory.LazyFunction(get_rss_channel_name),
            ),
        )
        local = factory.Trait(
            attributed_to=factory.SubFactory(
                federation_factories.ActorFactory, local=True
            ),
            library__privacy_level="everyone",
            artist__local=True,
        )


@registry.register(name="audio.Subscription")
class SubscriptionFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    uuid = factory.Faker("uuid4")
    approved = True
    target = factory.LazyAttribute(lambda o: ChannelFactory().actor)
    actor = factory.SubFactory(federation_factories.ActorFactory)

    class Meta:
        model = "federation.Follow"
