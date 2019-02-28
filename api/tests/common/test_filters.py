import pytest

from funkwhale_api.common import filters


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, True),
        ("True", True),
        ("true", True),
        ("1", True),
        ("yes", True),
        (False, False),
        ("False", False),
        ("false", False),
        ("0", False),
        ("no", False),
        ("None", None),
        ("none", None),
        ("Null", None),
        ("null", None),
    ],
)
def test_mutation_filter_is_approved(value, expected, factories):
    mutations = {
        True: factories["common.Mutation"](is_approved=True, payload={}),
        False: factories["common.Mutation"](is_approved=False, payload={}),
        None: factories["common.Mutation"](is_approved=None, payload={}),
    }

    qs = mutations[True].__class__.objects.all()

    filterset = filters.MutationFilter(
        {"q": "is_approved:{}".format(value)}, queryset=qs
    )

    assert list(filterset.qs) == [mutations[expected]]
