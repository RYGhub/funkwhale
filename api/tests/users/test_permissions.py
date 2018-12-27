import pytest
from rest_framework.views import APIView

from funkwhale_api.users import permissions


def test_has_user_permission_no_user(api_request):
    view = APIView.as_view()
    permission = permissions.HasUserPermission()
    request = api_request.get("/")
    assert permission.has_permission(request, view) is False


def test_has_user_permission_anonymous(anonymous_user, api_request):
    view = APIView.as_view()
    permission = permissions.HasUserPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    assert permission.has_permission(request, view) is False


@pytest.mark.parametrize("value", [True, False])
def test_has_user_permission_logged_in_single(value, factories, api_request):
    user = factories["users.User"](permission_moderation=value)

    class View(APIView):
        required_permissions = ["moderation"]

    view = View()
    permission = permissions.HasUserPermission()
    request = api_request.get("/")
    setattr(request, "user", user)
    result = permission.has_permission(request, view)
    assert result == user.has_permissions("moderation") == value


@pytest.mark.parametrize(
    "moderation,library,expected",
    [
        (True, False, False),
        (False, True, False),
        (False, False, False),
        (True, True, True),
    ],
)
def test_has_user_permission_logged_in_multiple_and(
    moderation, library, expected, factories, api_request
):
    user = factories["users.User"](
        permission_moderation=moderation, permission_library=library
    )

    class View(APIView):
        required_permissions = ["moderation", "library"]
        permission_operator = "and"

    view = View()
    permission = permissions.HasUserPermission()
    request = api_request.get("/")
    setattr(request, "user", user)
    result = permission.has_permission(request, view)
    assert result == user.has_permissions("moderation", "library") == expected


@pytest.mark.parametrize(
    "moderation,library,expected",
    [
        (True, False, True),
        (False, True, True),
        (False, False, False),
        (True, True, True),
    ],
)
def test_has_user_permission_logged_in_multiple_or(
    moderation, library, expected, factories, api_request
):
    user = factories["users.User"](
        permission_moderation=moderation, permission_library=library
    )

    class View(APIView):
        required_permissions = ["moderation", "library"]
        permission_operator = "or"

    view = View()
    permission = permissions.HasUserPermission()
    request = api_request.get("/")
    setattr(request, "user", user)
    result = permission.has_permission(request, view)
    has_permission_result = user.has_permissions("moderation", "library", operator="or")

    assert result == has_permission_result == expected
