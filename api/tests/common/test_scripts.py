import pytest

from funkwhale_api.common.management.commands import script
from funkwhale_api.common import scripts


@pytest.fixture
def command():
    return script.Command()


@pytest.mark.parametrize('script_name', [
    'django_permissions_to_user_permissions',
    'test',
])
def test_script_command_list(command, script_name, mocker):
    mocked = mocker.patch(
        'funkwhale_api.common.scripts.{}.main'.format(script_name))

    command.handle(script_name=script_name, interactive=False)

    mocked.assert_called_once_with(
        command, script_name=script_name, interactive=False)


def test_django_permissions_to_user_permissions(factories, command):
    group = factories['auth.Group'](
        perms=[
            'federation.change_library'
        ]
    )
    user1 = factories['users.User'](
        perms=[
            'dynamic_preferences.change_globalpreferencemodel',
            'music.add_importbatch',
        ]
    )
    user2 = factories['users.User'](
        perms=[
            'music.add_importbatch',
        ],
        groups=[group]
    )

    scripts.django_permissions_to_user_permissions.main(command)

    user1.refresh_from_db()
    user2.refresh_from_db()

    assert user1.permission_settings is True
    assert user1.permission_library is True
    assert user1.permission_federation is False

    assert user2.permission_settings is False
    assert user2.permission_library is True
    assert user2.permission_federation is True
