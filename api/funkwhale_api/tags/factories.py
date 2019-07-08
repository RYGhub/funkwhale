import factory

from funkwhale_api.factories import registry, NoUpdateOnCreate


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
