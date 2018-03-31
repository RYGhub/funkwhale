import factory
import requests
import requests_http_signature

from funkwhale_api.factories import registry

from . import keys


registry.register(keys.get_key_pair, name='federation.KeyPair')


@registry.register(name='federation.SignatureAuth')
class SignatureAuthFactory(factory.Factory):
    algorithm = 'rsa-sha256'
    key = factory.LazyFunction(lambda: keys.get_key_pair()[0])
    key_id = factory.Faker('url')
    use_auth_header = False
    headers = [
        '(request-target)',
        'user-agent',
        'host',
        'date',
        'content-type',]
    class Meta:
        model = requests_http_signature.HTTPSignatureAuth


@registry.register(name='federation.SignedRequest')
class SignedRequestFactory(factory.Factory):
    url = factory.Faker('url')
    method = 'get'
    auth = factory.SubFactory(SignatureAuthFactory)

    class Meta:
        model = requests.Request

    @factory.post_generation
    def headers(self, create, extracted, **kwargs):
        default_headers = {
            'User-Agent': 'Test',
            'Host': 'test.host',
            'Date': 'Right now',
            'Content-Type': 'application/activity+json'
        }
        if extracted:
            default_headers.update(extracted)
        self.headers.update(default_headers)


# @registry.register
# class ActorFactory(factory.DjangoModelFactory):
#     url = factory.Faker('url')
#     inbox_url = factory.Faker('url')
#     outbox_url = factory.Faker('url')
#     public_key = factory.LazyFunction(lambda: keys.get_key_pair()[1])
#     preferred_username = factory.Faker('username')
#     summary = factory.Faker('paragraph')
#
#     class Meta:
#         model = models.Actor
