from test_plus.test import TestCase
from rest_framework_jwt.settings import api_settings

from funkwhale_api.users.models import User


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class TestJWTQueryString(TestCase):
    www_authenticate_realm = 'api'

    def test_can_authenticate_using_token_param_in_url(self):
        user = User.objects.create_superuser(
            username='test', email='test@test.com', password='test')

        url = self.reverse('api:v1:tracks-list')
        with self.settings(API_AUTHENTICATION_REQUIRED=True):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        print(payload, token)
        with self.settings(API_AUTHENTICATION_REQUIRED=True):
            response = self.client.get(url, data={
                'jwt': token
            })

            self.assertEqual(response.status_code, 200)
