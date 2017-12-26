
def test__str__(factories):
    user = factories['users.User'](username='hello')
    assert user.__str__() == 'hello'
