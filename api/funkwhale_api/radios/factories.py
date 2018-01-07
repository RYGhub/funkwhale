import factory

from funkwhale_api.factories import registry
from funkwhale_api.users.factories import UserFactory


@registry.register
class RadioFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    description = factory.Faker('paragraphs')
    user = factory.SubFactory(UserFactory)
    config = []

    class Meta:
        model = 'radios.Radio'


@registry.register
class RadioSessionFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'radios.RadioSession'


@registry.register(name='radios.CustomRadioSession')
class RadioSessionFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    radio_type = 'custom'
    custom_radio = factory.SubFactory(
        RadioFactory, user=factory.SelfAttribute('..user'))

    class Meta:
        model = 'radios.RadioSession'
