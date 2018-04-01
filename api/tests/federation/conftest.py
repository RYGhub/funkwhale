import pytest


@pytest.fixture
def authenticated_actor(nodb_factories, mocker):
    actor = nodb_factories['federation.Actor']()
    mocker.patch(
        'funkwhale_api.federation.authentication.SignatureAuthentication.authenticate_actor',
        return_value=actor)
    yield actor
