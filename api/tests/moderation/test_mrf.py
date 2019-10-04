from funkwhale_api.moderation import mrf


def test_mrf_inbox_registry_apply_empty(mrf_inbox_registry, mocker):
    payload = {"hello": "world"}
    new_payload, updated = mrf_inbox_registry.apply(payload)

    assert new_payload == payload
    assert updated is False


def test_mrf_inbox_registry_apply_simple(mrf_inbox_registry, mocker):
    rule = mocker.Mock(return_value="test")
    payload = {"hello": "world"}
    mrf_inbox_registry.register(rule, name="rule")

    new_payload, updated = mrf_inbox_registry.apply(payload)

    assert new_payload == "test"
    assert updated is True


def test_mrf_inbox_registry_apply_skipped(mrf_inbox_registry, mocker):
    rule = mocker.Mock(side_effect=mrf.Skip())
    payload = {"hello": "world"}
    mrf_inbox_registry.register(rule, name="rule")

    new_payload, updated = mrf_inbox_registry.apply(payload)

    assert new_payload == payload
    assert updated is False


def test_mrf_inbox_registry_apply_discard(mrf_inbox_registry, mocker):
    rule1 = mocker.Mock(return_value=None)
    rule2 = mocker.Mock(side_effect=mrf.Discard())

    mrf_inbox_registry.register(rule1, name="rule1")
    mrf_inbox_registry.register(rule2, name="rule2")

    payload = {"hello": "world"}
    assert mrf_inbox_registry.apply(payload, arg1="value1") == (None, False)

    rule1.assert_called_once_with(payload, arg1="value1")
    rule2.assert_called_once_with(payload, arg1="value1")


def test_mrf_inbox_registry_use_returned_payload(mrf_inbox_registry, mocker):
    rule1 = mocker.Mock(return_value="payload1")
    rule2 = mocker.Mock(return_value="payload2")

    mrf_inbox_registry.register(rule1, name="rule1")
    mrf_inbox_registry.register(rule2, name="rule2")

    payload = {"hello": "world"}

    assert mrf_inbox_registry.apply(payload) == ("payload2", True)
    rule1.assert_called_once_with(payload)
    rule2.assert_called_once_with("payload1")


def test_mrf_inbox_registry_skip_errors(mrf_inbox_registry, mocker):
    rule1 = mocker.Mock(side_effect=Exception())

    mrf_inbox_registry.register(rule1, name="rule1")

    assert mrf_inbox_registry.apply("payload") == ("payload", False)
