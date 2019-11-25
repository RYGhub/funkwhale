import pytest

from click.testing import CliRunner

from funkwhale_api.cli import main
from funkwhale_api.cli import users


@pytest.mark.parametrize(
    "cmd, args, handlers",
    [
        (
            ("users", "create"),
            (
                "--username",
                "testuser",
                "--password",
                "testpassword",
                "--email",
                "test@hello.com",
                "--upload-quota",
                "35",
                "--permission",
                "library",
                "--permission",
                "moderation",
                "--staff",
                "--superuser",
            ),
            [
                (
                    users,
                    "handler_create_user",
                    {
                        "username": "testuser",
                        "password": "testpassword",
                        "email": "test@hello.com",
                        "upload_quota": 35,
                        "permissions": ("library", "moderation"),
                        "is_staff": True,
                        "is_superuser": True,
                    },
                )
            ],
        ),
        (
            ("users", "rm"),
            ("testuser1", "testuser2", "--no-input"),
            [
                (
                    users,
                    "handler_delete_user",
                    {"usernames": ("testuser1", "testuser2"), "soft": True},
                )
            ],
        ),
        (
            ("users", "rm"),
            ("testuser1", "testuser2", "--no-input", "--hard",),
            [
                (
                    users,
                    "handler_delete_user",
                    {"usernames": ("testuser1", "testuser2"), "soft": False},
                )
            ],
        ),
        (
            ("users", "set"),
            (
                "testuser1",
                "testuser2",
                "--no-input",
                "--inactive",
                "--upload-quota",
                "35",
                "--no-staff",
                "--superuser",
                "--permission-library",
                "--no-permission-moderation",
                "--no-permission-settings",
                "--password",
                "newpassword",
            ),
            [
                (
                    users,
                    "handler_update_user",
                    {
                        "usernames": ("testuser1", "testuser2"),
                        "kwargs": {
                            "is_active": False,
                            "upload_quota": 35,
                            "is_staff": False,
                            "is_superuser": True,
                            "permission_library": True,
                            "permission_moderation": False,
                            "permission_settings": False,
                            "password": "newpassword",
                        },
                    },
                )
            ],
        ),
    ],
)
def test_cli(cmd, args, handlers, mocker):
    patched_handlers = {}
    for module, path, _ in handlers:
        patched_handlers[(module, path)] = mocker.spy(module, path)

    runner = CliRunner()
    result = runner.invoke(main.base.cli, cmd + args)

    assert result.exit_code == 0, result.output

    for module, path, expected_call in handlers:
        patched_handlers[(module, path)].assert_called_once_with(**expected_call)
