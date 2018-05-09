
def test__str__(factories):
    user = factories['users.User'](username='hello')
    assert user.__str__() == 'hello'


def test_changing_password_updates_subsonic_api_token_no_token(factories):
    user = factories['users.User'](subsonic_api_token=None)
    user.set_password('new')
    assert user.subsonic_api_token is None


def test_changing_password_updates_subsonic_api_token(factories):
    user = factories['users.User'](subsonic_api_token='test')
    user.set_password('new')

    assert user.subsonic_api_token is not None
    assert user.subsonic_api_token != 'test'
