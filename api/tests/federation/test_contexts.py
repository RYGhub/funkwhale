import pytest

from funkwhale_api.federation import contexts


@pytest.mark.parametrize(
    "ns, property, expected",
    [
        ("AS", "followers", "https://www.w3.org/ns/activitystreams#followers"),
        ("AS", "following", "https://www.w3.org/ns/activitystreams#following"),
        ("SEC", "owner", "https://w3id.org/security#owner"),
        ("SEC", "publicKey", "https://w3id.org/security#publicKey"),
    ],
)
def test_context_ns(ns, property, expected):
    ns = getattr(contexts, ns)
    id = getattr(ns, property)
    assert id == expected


def test_raise_on_wrong_attr():
    ns = contexts.AS
    with pytest.raises(AttributeError):
        ns.noop


@pytest.mark.parametrize(
    "property, expected",
    [("publicKey", "_:publicKey"), ("cover", "_:cover"), ("hello", "_:hello")],
)
def test_noop_context(property, expected):
    assert getattr(contexts.NOOP, property) == expected
