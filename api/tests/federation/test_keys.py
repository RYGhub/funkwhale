from funkwhale_api.federation import keys


def test_public_key_fetching(r_mock):
    payload = {
        'id': 'https://actor.mock/users/actor#main-key',
        'owner': 'test',
        'publicKeyPem': 'test_pem',
    }
    actor = 'https://actor.mock/'
    r_mock.get(actor, json={'publicKey': payload})
    r = keys.get_public_key(actor)

    assert r['id'] == payload['id']
    assert r['owner'] == payload['owner']
    assert r['public_key_pem'] == payload['publicKeyPem']
