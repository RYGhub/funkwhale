import factory
from django.contrib.auth.models import Permission
from django.utils import timezone

from funkwhale_api.factories import ManyToManyFromList, registry, NoUpdateOnCreate

from . import models


@registry.register
class GroupFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "group-{0}".format(n))

    class Meta:
        model = "auth.Group"

    @factory.post_generation
    def perms(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            perms = [
                Permission.objects.get(
                    content_type__app_label=p.split(".")[0], codename=p.split(".")[1]
                )
                for p in extracted
            ]
            # A list of permissions were passed in, use them
            self.permissions.add(*perms)


@registry.register
class InvitationFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    owner = factory.LazyFunction(lambda: UserFactory())

    class Meta:
        model = "users.Invitation"

    class Params:
        expired = factory.Trait(expiration_date=factory.LazyFunction(timezone.now))


@registry.register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "user-{0}".format(n))
    email = factory.Sequence(lambda n: "user-{0}@example.com".format(n))
    password = factory.PostGenerationMethodCall("set_password", "test")
    subsonic_api_token = None
    groups = ManyToManyFromList("groups")
    avatar = factory.django.ImageField()

    class Meta:
        model = "users.User"
        django_get_or_create = ("username",)

    class Params:
        invited = factory.Trait(invitation=factory.SubFactory(InvitationFactory))

    @factory.post_generation
    def perms(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            perms = [
                Permission.objects.get(
                    content_type__app_label=p.split(".")[0], codename=p.split(".")[1]
                )
                for p in extracted
            ]
            # A list of permissions were passed in, use them
            self.user_permissions.add(*perms)

    @factory.post_generation
    def with_actor(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.actor = models.create_actor(self)
        self.save(update_fields=["actor"])
        return self.actor


@registry.register(name="users.SuperUser")
class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
