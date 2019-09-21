import pytest

from funkwhale_api.users import serializers


@pytest.mark.parametrize(
    "data, expected_error",
    [
        (
            {
                "username": "myusername",
                "email": "test@hello.com",
                "password1": "myusername",
            },
            r".*password is too similar.*",
        ),
        (
            {"username": "myusername", "email": "test@hello.com", "password1": "test"},
            r".*must contain at least 8 characters.*",
        ),
        (
            {
                "username": "myusername",
                "email": "test@hello.com",
                "password1": "superman",
            },
            r".*password is too common.*",
        ),
        (
            {
                "username": "myusername",
                "email": "test@hello.com",
                "password1": "123457809878",
            },
            r".*password is entirely numeric.*",
        ),
    ],
)
def test_registration_serializer_validates_password_properly(data, expected_error, db):
    data["password2"] = data["password1"]
    serializer = serializers.RegisterSerializer(data=data)

    with pytest.raises(serializers.serializers.ValidationError, match=expected_error):
        serializer.is_valid(raise_exception=True)
