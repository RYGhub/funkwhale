import json

from django.core.management import call_command


def test_mrf_check_inbox_all(mocker, mrf_inbox_registry, tmpfile):
    payload = {"hello": "world"}
    tmpfile.write(json.dumps(payload).encode())
    tmpfile.flush()
    apply = mocker.spy(mrf_inbox_registry, "apply")
    policy1 = mocker.Mock()
    policy2 = mocker.Mock(return_value={"hello": "noop"})
    mrf_inbox_registry.register(name="policy1")(policy1)
    mrf_inbox_registry.register(name="policy2")(policy2)

    call_command("mrf_check", "inbox", tmpfile.name)

    apply.assert_called_once_with(payload, policies=[])
    policy1.assert_called_once_with(payload)
    policy2.assert_called_once_with(policy1.return_value)


def test_mrf_check_inbox_list(mocker, mrf_inbox_registry):
    apply = mocker.spy(mrf_inbox_registry, "apply")
    policy1 = mocker.Mock()
    policy2 = mocker.Mock(return_value={"hello": "noop"})
    mrf_inbox_registry.register(name="policy1")(policy1)
    mrf_inbox_registry.register(name="policy2")(policy2)

    call_command("mrf_check", "inbox")

    apply.assert_not_called()


def test_mrf_check_inbox_restrict_policies(mocker, mrf_inbox_registry, tmpfile):
    payload = {"hello": "world"}
    tmpfile.write(json.dumps(payload).encode())
    tmpfile.flush()
    apply = mocker.spy(mrf_inbox_registry, "apply")
    policy1 = mocker.Mock()
    policy2 = mocker.Mock()
    policy3 = mocker.Mock(return_value={"hello": "noop"})
    mrf_inbox_registry.register(name="policy1")(policy1)
    mrf_inbox_registry.register(name="policy2")(policy2)
    mrf_inbox_registry.register(name="policy3")(policy3)

    call_command("mrf_check", "inbox", tmpfile.name, policies=["policy1", "policy3"])

    apply.assert_called_once_with(payload, policies=["policy1", "policy3"])
    policy1.assert_called_once_with(payload)
    policy2.assert_not_called()
    policy3.assert_called_once_with(policy1.return_value)


def test_mrf_check_inbox_db_activity(factories, mocker, mrf_inbox_registry):
    payload = {"hello": "world"}
    activity = factories["federation.Activity"](payload=payload)

    policy1 = mocker.Mock(return_value={"hello": "noop"})
    mrf_inbox_registry.register(name="policy1")(policy1)

    call_command("mrf_check", "inbox", activity.uuid)

    policy1.assert_called_once_with(payload)


def test_mrf_check_inbox_url(r_mock, mocker, mrf_inbox_registry):
    payload = {"hello": "world"}
    url = "http://test.hello/path"
    r_mock.get(url, json=payload)

    policy1 = mocker.Mock(return_value={"hello": "noop"})
    mrf_inbox_registry.register(name="policy1")(policy1)

    call_command("mrf_check", "inbox", url)

    policy1.assert_called_once_with(payload)
