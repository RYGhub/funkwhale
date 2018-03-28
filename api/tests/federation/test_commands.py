from django.core.management import call_command


def test_generate_instance_key_pair(preferences, mocker):
    mocker.patch(
        'funkwhale_api.federation.keys.get_key_pair',
        return_value=(b'private', b'public'))
    assert preferences['federation__public_key'] == ''
    assert preferences['federation__private_key'] == ''

    call_command('generate_keys', interactive=False)

    assert preferences['federation__private_key'] == 'private'
    assert preferences['federation__public_key'] == 'public'
