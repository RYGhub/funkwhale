from rest_framework import serializers
import pytest

from django.core.exceptions import ObjectDoesNotExist

from funkwhale_api.federation import exceptions, utils


@pytest.mark.parametrize(
    "url,path,expected",
    [
        ("http://test.com", "/hello", "http://test.com/hello"),
        ("http://test.com/", "hello", "http://test.com/hello"),
        ("http://test.com/", "/hello", "http://test.com/hello"),
        ("http://test.com", "hello", "http://test.com/hello"),
    ],
)
def test_full_url(settings, url, path, expected):
    settings.FUNKWHALE_URL = url
    assert utils.full_url(path) == expected


def test_extract_headers_from_meta():
    wsgi_headers = {
        "HTTP_HOST": "nginx",
        "HTTP_X_REAL_IP": "172.20.0.4",
        "HTTP_X_FORWARDED_FOR": "188.165.228.227, 172.20.0.4",
        "HTTP_X_FORWARDED_PROTO": "http",
        "HTTP_X_FORWARDED_HOST": "localhost:80",
        "HTTP_X_FORWARDED_PORT": "80",
        "HTTP_CONNECTION": "close",
        "CONTENT_LENGTH": "1155",
        "CONTENT_TYPE": "txt/application",
        "HTTP_SIGNATURE": "Hello",
        "HTTP_DATE": "Sat, 31 Mar 2018 13:53:55 GMT",
        "HTTP_USER_AGENT": "http.rb/3.0.0 (Mastodon/2.2.0; +https://mastodon.eliotberriot.com/)",
    }

    cleaned_headers = utils.clean_wsgi_headers(wsgi_headers)

    expected = {
        "Host": "nginx",
        "X-Real-Ip": "172.20.0.4",
        "X-Forwarded-For": "188.165.228.227, 172.20.0.4",
        "X-Forwarded-Proto": "http",
        "X-Forwarded-Host": "localhost:80",
        "X-Forwarded-Port": "80",
        "Connection": "close",
        "Content-Length": "1155",
        "Content-Type": "txt/application",
        "Signature": "Hello",
        "Date": "Sat, 31 Mar 2018 13:53:55 GMT",
        "User-Agent": "http.rb/3.0.0 (Mastodon/2.2.0; +https://mastodon.eliotberriot.com/)",
    }
    assert cleaned_headers == expected


def test_retrieve_ap_object(db, r_mock):
    fid = "https://some.url"
    m = r_mock.get(fid, json={"hello": "world"})
    result = utils.retrieve_ap_object(fid, actor=None)

    assert result == {"hello": "world"}
    assert m.request_history[-1].headers["Accept"] == "application/activity+json"


def test_retrieve_ap_object_honor_instance_policy_domain(factories):
    domain = factories["moderation.InstancePolicy"](
        block_all=True, for_domain=True
    ).target_domain
    fid = "https://{}/test".format(domain.name)

    with pytest.raises(exceptions.BlockedActorOrDomain):
        utils.retrieve_ap_object(fid, actor=None)


def test_retrieve_ap_object_honor_mrf_inbox_before_http(
    mrf_inbox_registry, factories, mocker
):
    apply = mocker.patch.object(mrf_inbox_registry, "apply", return_value=(None, False))
    fid = "http://domain/test"
    with pytest.raises(exceptions.BlockedActorOrDomain):
        utils.retrieve_ap_object(fid, actor=None)

    apply.assert_called_once_with({"id": fid})


def test_retrieve_ap_object_honor_mrf_inbox_after_http(
    r_mock, mrf_inbox_registry, factories, mocker
):
    apply = mocker.patch.object(
        mrf_inbox_registry, "apply", side_effect=[(True, False), (None, False)]
    )
    payload = {"id": "http://domain/test", "actor": "hello"}
    r_mock.get(payload["id"], json=payload)
    with pytest.raises(exceptions.BlockedActorOrDomain):
        utils.retrieve_ap_object(payload["id"], actor=None)

    apply.assert_any_call({"id": payload["id"]})
    apply.assert_any_call(payload)


def test_retrieve_ap_object_honor_instance_policy_different_url_and_id(
    r_mock, factories
):
    domain = factories["moderation.InstancePolicy"](
        block_all=True, for_domain=True
    ).target_domain
    fid = "https://ok/test"
    r_mock.get(fid, json={"id": "http://{}/test".format(domain.name)})

    with pytest.raises(exceptions.BlockedActorOrDomain):
        utils.retrieve_ap_object(fid, actor=None)


def test_retrieve_with_actor(r_mock, factories):
    actor = factories["federation.Actor"]()
    fid = "https://some.url"
    m = r_mock.get(fid, json={"hello": "world"})
    result = utils.retrieve_ap_object(fid, actor=actor)

    assert result == {"hello": "world"}
    assert m.request_history[-1].headers["Accept"] == "application/activity+json"
    assert m.request_history[-1].headers["Signature"] is not None


def test_retrieve_with_queryset(factories):
    actor = factories["federation.Actor"]()

    assert utils.retrieve_ap_object(actor.fid, actor=None, queryset=actor.__class__)


def test_retrieve_with_serializer(db, r_mock):
    class S(serializers.Serializer):
        def create(self, validated_data):
            return {"persisted": "object"}

    fid = "https://some.url"
    r_mock.get(fid, json={"hello": "world"})
    result = utils.retrieve_ap_object(fid, actor=None, serializer_class=S)

    assert result == {"persisted": "object"}


@pytest.mark.parametrize(
    "factory_name, fids, kwargs, expected_indexes",
    [
        (
            "music.Artist",
            ["https://local.domain/test", "http://local.domain/"],
            {},
            [0, 1],
        ),
        (
            "music.Artist",
            ["https://local.domain/test", "http://notlocal.domain/"],
            {},
            [0],
        ),
        (
            "music.Artist",
            ["https://local.domain/test", "http://notlocal.domain/"],
            {"include": False},
            [1],
        ),
    ],
)
def test_local_qs(factory_name, fids, kwargs, expected_indexes, factories, settings):
    settings.FEDERATION_HOSTNAME = "local.domain"
    objs = [factories[factory_name](fid=fid) for fid in fids]

    qs = objs[0].__class__.objects.all().order_by("id")
    result = utils.local_qs(qs, **kwargs)

    expected_objs = [obj for i, obj in enumerate(objs) if i in expected_indexes]
    assert list(result) == expected_objs


def test_get_obj_by_fid_not_found():
    with pytest.raises(ObjectDoesNotExist):
        utils.get_object_by_fid("http://test")


def test_get_obj_by_fid_local_not_found(factories):
    obj = factories["federation.Actor"](local=False)
    with pytest.raises(ObjectDoesNotExist):
        utils.get_object_by_fid(obj.fid, local=True)


def test_get_obj_by_fid_local(factories):
    obj = factories["federation.Actor"](local=True)
    assert utils.get_object_by_fid(obj.fid, local=True) == obj


@pytest.mark.parametrize(
    "factory_name",
    [
        "federation.Actor",
        "music.Artist",
        "music.Album",
        "music.Track",
        "music.Upload",
        "music.Library",
    ],
)
def test_get_obj_by_fid(factory_name, factories):
    obj = factories[factory_name]()
    factories[factory_name]()
    assert utils.get_object_by_fid(obj.fid) == obj


def test_get_channel_by_fid(factories):
    obj = factories["audio.Channel"]()
    factories["audio.Channel"]()
    assert utils.get_object_by_fid(obj.actor.fid) == obj
