import pytest
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q

from funkwhale_api.common import fields
from funkwhale_api.users.factories import UserFactory


@pytest.mark.parametrize(
    "user,expected",
    [
        (AnonymousUser(), Q(privacy_level="everyone")),
        (
            UserFactory.build(pk=1),
            Q(privacy_level__in=["instance", "everyone"])
            | Q(privacy_level="me", user=UserFactory.build(pk=1)),
        ),
    ],
)
def test_privacy_level_query(user, expected):
    query = fields.privacy_level_query(user)
    assert query == expected


def test_generic_relation_field(factories):
    obj = factories["users.User"]()
    f = fields.GenericRelation(
        {
            "user": {
                "queryset": obj.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        }
    )

    data = {"type": "user", "username": obj.username}

    assert f.to_internal_value(data) == obj


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        ({}, r".*Invalid data.*"),
        (1, r".*Invalid data.*"),
        (False, r".*Invalid data.*"),
        ("test", r".*Invalid data.*"),
        ({"missing": "type"}, r".*Invalid type.*"),
        ({"type": "noop"}, r".*Invalid type.*"),
        ({"type": "user"}, r".*Invalid username.*"),
        ({"type": "user", "username": {}}, r".*Invalid username.*"),
        ({"type": "user", "username": "not_found"}, r".*Object not found.*"),
    ],
)
def test_generic_relation_field_validation_error(payload, expected_error, factories):
    obj = factories["users.User"]()
    f = fields.GenericRelation(
        {
            "user": {
                "queryset": obj.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        }
    )

    with pytest.raises(fields.serializers.ValidationError, match=expected_error):
        f.to_internal_value(payload)
