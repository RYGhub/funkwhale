import pytest

from funkwhale_api.common import pagination


@pytest.mark.parametrize(
    "view_max_page_size, view_default_page_size, request_page_size, expected",
    [
        (50, 50, None, 50),
        (50, 25, None, 25),
        (25, None, None, 25),
        (50, 25, 100, 50),
        (50, None, 100, 50),
        (50, 25, 33, 33),
    ],
)
def test_funkwhale_pagination_uses_view_page_size(
    view_max_page_size, view_default_page_size, request_page_size, expected, mocker
):
    p = pagination.FunkwhalePagination()

    p.view = mocker.Mock(
        max_page_size=view_max_page_size, default_page_size=view_default_page_size
    )
    query = {}
    if request_page_size:
        query["page_size"] = request_page_size
    request = mocker.Mock(query_params=query)
    assert p.get_page_size(request) == expected
