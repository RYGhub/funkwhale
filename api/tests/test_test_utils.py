from . import utils as test_utils


def test_to_api_date(now):

    assert test_utils.to_api_date(now) == now.isoformat().split("+")[0] + "Z"
