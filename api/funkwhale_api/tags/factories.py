import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate

from . import models


@registry.register
class TagFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.Faker("music_hashtag")

    class Meta:
        model = "tags.Tag"


@registry.register
class TaggedItemFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    tag = factory.SubFactory(TagFactory)
    content_object = None

    class Meta:
        model = "tags.TaggedItem"


class TaggableFactory(factory.django.DjangoModelFactory):
    @factory.post_generation
    def set_tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            models.set_tags(self, *extracted)
