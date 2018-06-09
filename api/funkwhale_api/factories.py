import factory
import persisting_theory


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
