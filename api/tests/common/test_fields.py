import pytest

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q

from funkwhale_api.common import fields
from funkwhale_api.users.factories import UserFactory


@pytest.mark.parametrize('user,expected', [
    (AnonymousUser(), Q(privacy_level='everyone')),
    (UserFactory.build(pk=1),
     Q(privacy_level__in=['followers', 'instance', 'everyone'])),
])
def test_privacy_level_query(user,expected):
    query = fields.privacy_level_query(user)
    assert query == expected
