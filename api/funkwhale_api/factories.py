import uuid
import factory
import persisting_theory

from django.conf import settings

from faker.providers import internet as internet_provider


class FactoriesRegistry(persisting_theory.Registry):
    look_into = "factories"

    def prepare_name(self, data, name=None):
        return name or data._meta.model._meta.label


registry = FactoriesRegistry()


def ManyToManyFromList(field_name):
    """
    To automate the pattern described in
    http://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship
    """

    @factory.post_generation
    def inner(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            field = getattr(self, field_name)
            field.add(*extracted)

    return inner


class NoUpdateOnCreate:
    """
    Factory boy calls save after the initial create. In most case, this
    is not needed, so we disable this behaviour
    """

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        return


class FunkwhaleProvider(internet_provider.Provider):
    """
    Our own faker data generator, since built-in ones are sometimes
    not random enough
    """

    def federation_url(self, prefix="", local=False):
        def path_generator():
            return "{}/{}".format(prefix, uuid.uuid4())

        domain = settings.FEDERATION_HOSTNAME if local else self.domain_name()
        protocol = "https"
        path = path_generator()
        return "{}://{}/{}".format(protocol, domain, path)


factory.Faker.add_provider(FunkwhaleProvider)
