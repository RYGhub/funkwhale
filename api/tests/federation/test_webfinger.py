import pytest

from django import forms

from funkwhale_api.federation import webfinger


def test_webfinger_clean_resource():
    t, r = webfinger.clean_resource("acct:service@test.federation")
    assert t == "acct"
    assert r == "service@test.federation"


@pytest.mark.parametrize(
    "resource,message",
    [
        ("", "Invalid resource string"),
        ("service@test.com", "Missing webfinger resource type"),
        ("noop:service@test.com", "Invalid webfinger resource type"),
    ],
)
def test_webfinger_clean_resource_errors(resource, message):
    with pytest.raises(forms.ValidationError) as excinfo:
        webfinger.clean_resource(resource)

        assert message == str(excinfo)


def test_webfinger_clean_acct(settings):
    username, hostname = webfinger.clean_acct("library@test.federation")
    assert username == "library"
    assert hostname == "test.federation"


@pytest.mark.parametrize(
    "resource,message",
    [
        ("service", "Invalid format"),
        ("service@test.com", "Invalid hostname test.com"),
        ("noop@test.federation", "Invalid account"),
    ],
)
def test_webfinger_clean_acct_errors(resource, message, settings):
    with pytest.raises(forms.ValidationError) as excinfo:
        webfinger.clean_resource(resource)

        assert message == str(excinfo)


def test_webfinger_get_resource(r_mock):
    resource = "acct:test@test.webfinger"
    payload = {
        "subject": resource,
        "aliases": ["https://test.webfinger"],
        "links": [
            {
                "rel": "self",
                "type": "application/activity+json",
                "href": "https://test.webfinger/user/test",
            }
        ],
    }
    r_mock.get(
        "https://test.webfinger/.well-known/webfinger?resource={}".format(resource),
        json=payload,
    )

    data = webfinger.get_resource("acct:test@test.webfinger")

    assert data["actor_url"] == "https://test.webfinger/user/test"
    assert data["subject"] == resource
