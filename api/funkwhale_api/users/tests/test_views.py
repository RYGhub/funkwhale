import json

from django.test import RequestFactory

from test_plus.test import TestCase
from funkwhale_api.users.models import User

from . factories import UserFactory


class UserTestCase(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.factory = RequestFactory()

    def test_can_create_user_via_api(self):
        url = self.reverse('rest_register')
        data = {
            'username': 'test1',
            'email': 'test1@test.com',
            'password1': 'testtest',
            'password2': 'testtest',
        }
        with self.settings(REGISTRATION_MODE="public"):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        u = User.objects.get(email='test1@test.com')
        self.assertEqual(u.username, 'test1')

    def test_can_disable_registration_view(self):
        url = self.reverse('rest_register')
        data = {
            'username': 'test1',
            'email': 'test1@test.com',
            'password1': 'testtest',
            'password2': 'testtest',
        }
        with self.settings(REGISTRATION_MODE="disabled"):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_can_fetch_data_from_api(self):
        url = self.reverse('api:users:users-me')
        response = self.client.get(url)
        # login required
        self.assertEqual(response.status_code, 401)

        user = UserFactory(is_staff=True, perms=['music.add_importbatch'])
        self.assertTrue(user.has_perm('music.add_importbatch'))
        self.login(user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))

        self.assertEqual(payload['username'], user.username)
        self.assertEqual(payload['is_staff'], user.is_staff)
        self.assertEqual(payload['is_superuser'], user.is_superuser)
        self.assertEqual(payload['email'], user.email)
        self.assertEqual(payload['name'], user.name)
        self.assertEqual(
            payload['permissions']['import.launch']['status'], True)
