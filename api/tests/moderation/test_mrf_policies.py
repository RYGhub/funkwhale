import pytest

from funkwhale_api.moderation import mrf
from funkwhale_api.moderation import mrf_policies


@pytest.mark.parametrize(
    "enabled, payload, kwargs, allowed_domains, expected",
    [
        # allow listing enabled, domain on allowed list -> nothing happens
        (
            True,
            {"id": "http://allowed.example"},
            {"sender_id": "http://allowed.example/actor"},
            ["allowed.example"],
            None,
        ),
        # allow listing enabled, domain NOT on allowed list -> message discarded
        (
            True,
            {"id": "http://notallowed.example"},
            {"sender_id": "http://notallowed.example/actor"},
            ["allowed.example"],
            mrf.Discard,
        ),
        # allow listing disabled -> policy skipped
        (
            False,
            {"id": "http://allowed.example"},
            {"sender_id": "http://allowed.example/actor"},
            [],
            mrf.Skip,
        ),
        # multiple domains to check, one is not allowed -> message discarded
        (
            True,
            {"id": "http://allowed.example"},
            {"sender_id": "http://notallowed.example/actor"},
            ["allowed.example"],
            mrf.Discard,
        ),
        # multiple domains to check, all allowed -> nothing happens
        (
            True,
            {"id": "http://allowed.example"},
            {"sender_id": "http://anotherallowed.example/actor"},
            ["allowed.example", "anotherallowed.example"],
            None,
        ),
    ],
)
def test_allow_list_policy(
    enabled, payload, kwargs, expected, allowed_domains, preferences, factories
):
    preferences["moderation__allow_list_enabled"] = enabled
    for d in allowed_domains:
        factories["federation.Domain"](name=d, allowed=True)

    if expected:
        with pytest.raises(expected):
            mrf_policies.check_allow_list(payload, **kwargs)
    else:
        assert mrf_policies.check_allow_list(payload, **kwargs) == expected
