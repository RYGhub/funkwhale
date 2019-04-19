from django.urls import reverse

from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import tasks as federation_tasks
from funkwhale_api.manage import serializers


def test_user_view(factories, superuser_api_client, mocker):
    mocker.patch("funkwhale_api.users.models.User.record_activity")
    users = factories["users.User"].create_batch(size=5) + [superuser_api_client.user]
    qs = users[0].__class__.objects.order_by("-id")
    url = reverse("api:v1:manage:users:users-list")

    response = superuser_api_client.get(url, {"sort": "-id"})
    expected = serializers.ManageUserSerializer(
        qs, many=True, context={"request": response.wsgi_request}
    ).data

    assert response.data["count"] == len(users)
    assert response.data["results"] == expected


def test_invitation_view(factories, superuser_api_client, mocker):
    invitations = factories["users.Invitation"].create_batch(size=5)
    qs = invitations[0].__class__.objects.order_by("-id")
    url = reverse("api:v1:manage:users:invitations-list")

    response = superuser_api_client.get(url, {"sort": "-id"})
    expected = serializers.ManageInvitationSerializer(qs, many=True).data

    assert response.data["count"] == len(invitations)
    assert response.data["results"] == expected


def test_invitation_view_create(factories, superuser_api_client, mocker):
    url = reverse("api:v1:manage:users:invitations-list")
    response = superuser_api_client.post(url)

    assert response.status_code == 201
    assert superuser_api_client.user.invitations.latest("id") is not None


def test_domain_list(factories, superuser_api_client, settings):
    factories["federation.Domain"](pk=settings.FEDERATION_HOSTNAME)
    d = factories["federation.Domain"]()
    url = reverse("api:v1:manage:federation:domains-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == d.pk


def test_domain_detail(factories, superuser_api_client):
    d = factories["federation.Domain"]()
    url = reverse("api:v1:manage:federation:domains-detail", kwargs={"pk": d.name})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["name"] == d.pk


def test_domain_create(superuser_api_client, mocker):
    update_domain_nodeinfo = mocker.patch(
        "funkwhale_api.federation.tasks.update_domain_nodeinfo"
    )
    url = reverse("api:v1:manage:federation:domains-list")
    response = superuser_api_client.post(url, {"name": "test.federation"})

    assert response.status_code == 201
    assert federation_models.Domain.objects.filter(pk="test.federation").exists()
    update_domain_nodeinfo.assert_called_once_with(domain_name="test.federation")


def test_domain_nodeinfo(factories, superuser_api_client, mocker):
    domain = factories["federation.Domain"]()
    url = reverse(
        "api:v1:manage:federation:domains-nodeinfo", kwargs={"pk": domain.name}
    )
    mocker.patch.object(
        federation_tasks, "fetch_nodeinfo", return_value={"hello": "world"}
    )
    update_domain_nodeinfo = mocker.spy(federation_tasks, "update_domain_nodeinfo")
    response = superuser_api_client.get(url)
    assert response.status_code == 200
    assert response.data == {"status": "ok", "payload": {"hello": "world"}}

    update_domain_nodeinfo.assert_called_once_with(domain_name=domain.name)


def test_domain_stats(factories, superuser_api_client, mocker):
    domain = factories["federation.Domain"]()
    mocker.patch.object(domain.__class__, "get_stats", return_value={"hello": "world"})
    url = reverse("api:v1:manage:federation:domains-stats", kwargs={"pk": domain.name})
    response = superuser_api_client.get(url)
    assert response.status_code == 200
    assert response.data == {"hello": "world"}


def test_actor_list(factories, superuser_api_client, settings):
    actor = factories["federation.Actor"]()
    url = reverse("api:v1:manage:accounts-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == actor.id


def test_actor_detail(factories, superuser_api_client):
    actor = factories["federation.Actor"]()
    url = reverse("api:v1:manage:accounts-detail", kwargs={"pk": actor.full_username})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == actor.id


def test_instance_policy_create(superuser_api_client, factories):
    domain = factories["federation.Domain"]()
    actor = superuser_api_client.user.create_actor()
    url = reverse("api:v1:manage:moderation:instance-policies-list")
    response = superuser_api_client.post(
        url,
        {"target": {"type": "domain", "id": domain.name}, "block_all": True},
        format="json",
    )

    assert response.status_code == 201

    policy = domain.instance_policy
    assert policy.actor == actor


def test_artist_list(factories, superuser_api_client, settings):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:manage:library:artists-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == artist.id


def test_artist_detail(factories, superuser_api_client):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:manage:library:artists-detail", kwargs={"pk": artist.pk})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == artist.id


def test_artist_detail_stats(factories, superuser_api_client):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:manage:library:artists-stats", kwargs={"pk": artist.pk})
    response = superuser_api_client.get(url)
    expected = {
        "libraries": 0,
        "uploads": 0,
        "listenings": 0,
        "playlists": 0,
        "mutations": 0,
        "track_favorites": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_artist_delete(factories, superuser_api_client):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:manage:library:artists-detail", kwargs={"pk": artist.pk})
    response = superuser_api_client.delete(url)

    assert response.status_code == 204


def test_album_list(factories, superuser_api_client, settings):
    album = factories["music.Album"]()
    factories["music.Album"]()
    url = reverse("api:v1:manage:library:albums-list")
    response = superuser_api_client.get(
        url, {"q": 'artist:"{}"'.format(album.artist.name)}
    )

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == album.id


def test_album_detail(factories, superuser_api_client):
    album = factories["music.Album"]()
    url = reverse("api:v1:manage:library:albums-detail", kwargs={"pk": album.pk})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == album.id


def test_album_detail_stats(factories, superuser_api_client):
    album = factories["music.Album"]()
    url = reverse("api:v1:manage:library:albums-stats", kwargs={"pk": album.pk})
    response = superuser_api_client.get(url)
    expected = {
        "libraries": 0,
        "uploads": 0,
        "listenings": 0,
        "playlists": 0,
        "mutations": 0,
        "track_favorites": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_album_delete(factories, superuser_api_client):
    album = factories["music.Album"]()
    url = reverse("api:v1:manage:library:albums-detail", kwargs={"pk": album.pk})
    response = superuser_api_client.delete(url)

    assert response.status_code == 204


def test_track_list(factories, superuser_api_client, settings):
    track = factories["music.Track"]()
    url = reverse("api:v1:manage:library:tracks-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == track.id


def test_track_detail(factories, superuser_api_client):
    track = factories["music.Track"]()
    url = reverse("api:v1:manage:library:tracks-detail", kwargs={"pk": track.pk})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == track.id


def test_track_detail_stats(factories, superuser_api_client):
    track = factories["music.Track"]()
    url = reverse("api:v1:manage:library:tracks-stats", kwargs={"pk": track.pk})
    response = superuser_api_client.get(url)
    expected = {
        "libraries": 0,
        "uploads": 0,
        "listenings": 0,
        "playlists": 0,
        "mutations": 0,
        "track_favorites": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_track_delete(factories, superuser_api_client):
    track = factories["music.Track"]()
    url = reverse("api:v1:manage:library:tracks-detail", kwargs={"pk": track.pk})
    response = superuser_api_client.delete(url)

    assert response.status_code == 204


def test_library_list(factories, superuser_api_client, settings):
    library = factories["music.Library"]()
    url = reverse("api:v1:manage:library:libraries-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == library.id


def test_library_detail(factories, superuser_api_client):
    library = factories["music.Library"]()
    url = reverse(
        "api:v1:manage:library:libraries-detail", kwargs={"uuid": library.uuid}
    )
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == library.id


def test_library_detail_stats(factories, superuser_api_client):
    library = factories["music.Library"]()
    url = reverse(
        "api:v1:manage:library:libraries-stats", kwargs={"uuid": library.uuid}
    )
    response = superuser_api_client.get(url)
    expected = {
        "uploads": 0,
        "followers": 0,
        "tracks": 0,
        "albums": 0,
        "artists": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_library_delete(factories, superuser_api_client):
    library = factories["music.Library"]()
    url = reverse(
        "api:v1:manage:library:libraries-detail", kwargs={"uuid": library.uuid}
    )
    response = superuser_api_client.delete(url)

    assert response.status_code == 204


def test_upload_list(factories, superuser_api_client, settings):
    upload = factories["music.Upload"]()
    url = reverse("api:v1:manage:library:uploads-list")
    response = superuser_api_client.get(url)

    assert response.status_code == 200

    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == upload.id


def test_upload_detail(factories, superuser_api_client):
    upload = factories["music.Upload"]()
    url = reverse("api:v1:manage:library:uploads-detail", kwargs={"uuid": upload.uuid})
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == upload.id


def test_upload_delete(factories, superuser_api_client):
    upload = factories["music.Upload"]()
    url = reverse("api:v1:manage:library:uploads-detail", kwargs={"uuid": upload.uuid})
    response = superuser_api_client.delete(url)

    assert response.status_code == 204
