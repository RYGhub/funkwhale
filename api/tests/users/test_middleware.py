from funkwhale_api.users import middleware


def test_record_activity_middleware(factories, api_request, mocker):
    m = middleware.RecordActivityMiddleware(lambda request: None)
    user = factories["users.User"]()
    record_activity = mocker.patch("funkwhale_api.users.models.User.record_activity")
    request = api_request.get("/")
    request.user = user
    m(request)

    record_activity.assert_called_once_with()


def test_record_activity_middleware_no_user(api_request):
    m = middleware.RecordActivityMiddleware(lambda request: None)
    request = api_request.get("/")
    m(request)
