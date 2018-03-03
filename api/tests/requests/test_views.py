from django.urls import reverse


def test_request_viewset_requires_auth(db, api_client):
    url = reverse('api:v1:requests:import-requests-list')
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.parametrize('method', ['put', 'patch'])
def test_user_can_create_request(method, logged_in_api_client):
    url = reverse('api:v1:requests:import-requests-list')
    user = logged_in_api_client.user
    data = {
        'artist_name': 'System of a Down',
        'albums': 'All please!',
        'comment': 'Please, they rock!',
    }
    response = logged_in_api_client.post(url, data)

    assert response.status_code == 201

    ir = user.import_requests.latest('id')
    assert ir.status == 'pending'
    assert ir.creation_date is not None
    for field, value in data.items():
        assert getattr(ir, field) == value
