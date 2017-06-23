import factory

from django.contrib.auth.models import Permission


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username', )

    @factory.post_generation
    def perms(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            perms = [
                Permission.objects.get(
                    content_type__app_label=p.split('.')[0],
                    codename=p.split('.')[1],
                )
                for p in extracted
            ]
            # A list of permissions were passed in, use them
            self.user_permissions.add(*perms)
