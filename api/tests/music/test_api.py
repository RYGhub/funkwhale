import json
import os
import pytest
from django.urls import reverse

from funkwhale_api.music import models
from funkwhale_api.music import tasks


DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_can_submit_youtube_url_for_track_import(
    settings, artists, albums, tracks, mocker, superuser_client
):
    mocker.patch("funkwhale_api.music.tasks.import_job_run.delay")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get",
        return_value=artists["get"]["adhesive_wombat"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get"]["marsupial"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.get",
        return_value=tracks["get"]["8bitadventures"],
    )
    mocker.patch(
        "funkwhale_api.music.models.TrackFile.download_file", return_value=None
    )
    mbid = "9968a9d6-8d92-4051-8f76-674e157b6eed"
    video_id = "tPEE9ZwTmy0"
    url = reverse("api:v1:submit-single")
    video_url = "https://www.youtube.com/watch?v={0}".format(video_id)
    response = superuser_client.post(url, {"import_url": video_url, "mbid": mbid})

    assert response.status_code == 201
    batch = superuser_client.user.imports.latest("id")
    job = batch.jobs.latest("id")
    assert job.status == "pending"
    assert str(job.mbid) == mbid
    assert job.source == video_url


def test_import_creates_an_import_with_correct_data(mocker, superuser_client):
    mocker.patch("funkwhale_api.music.tasks.import_job_run")
    mbid = "9968a9d6-8d92-4051-8f76-674e157b6eed"
    video_id = "tPEE9ZwTmy0"
    url = reverse("api:v1:submit-single")
    response = superuser_client.post(
        url,
        {
            "import_url": "https://www.youtube.com/watch?v={0}".format(video_id),
            "mbid": mbid,
        },
    )

    batch = models.ImportBatch.objects.latest("id")
    assert batch.jobs.count() == 1
    assert batch.submitted_by == superuser_client.user
    assert batch.status == "pending"
    job = batch.jobs.first()
    assert str(job.mbid) == mbid
    assert job.status == "pending"
    assert job.source == "https://www.youtube.com/watch?v={0}".format(video_id)


def test_can_import_whole_album(artists, albums, mocker, superuser_client):
    mocker.patch("funkwhale_api.music.tasks.import_job_run")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get", return_value=artists["get"]["soad"]
    )
    mocker.patch("funkwhale_api.musicbrainz.api.images.get_front", return_value=b"")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get_with_includes"]["hypnotize"],
    )
    payload = {
        "releaseId": "47ae093f-1607-49a3-be11-a15d335ccc94",
        "tracks": [
            {
                "mbid": "1968a9d6-8d92-4051-8f76-674e157b6eed",
                "source": "https://www.youtube.com/watch?v=1111111111",
            },
            {
                "mbid": "2968a9d6-8d92-4051-8f76-674e157b6eed",
                "source": "https://www.youtube.com/watch?v=2222222222",
            },
            {
                "mbid": "3968a9d6-8d92-4051-8f76-674e157b6eed",
                "source": "https://www.youtube.com/watch?v=3333333333",
            },
        ],
    }
    url = reverse("api:v1:submit-album")
    response = superuser_client.post(
        url, json.dumps(payload), content_type="application/json"
    )

    batch = models.ImportBatch.objects.latest("id")
    assert batch.jobs.count() == 3
    assert batch.submitted_by == superuser_client.user
    assert batch.status == "pending"

    album = models.Album.objects.latest("id")
    assert str(album.mbid) == "47ae093f-1607-49a3-be11-a15d335ccc94"
    medium_data = albums["get_with_includes"]["hypnotize"]["release"]["medium-list"][0]
    assert int(medium_data["track-count"]) == album.tracks.all().count()

    for track in medium_data["track-list"]:
        instance = models.Track.objects.get(mbid=track["recording"]["id"])
        assert instance.title == track["recording"]["title"]
        assert instance.position == int(track["position"])
        assert instance.title == track["recording"]["title"]

    for row in payload["tracks"]:
        job = models.ImportJob.objects.get(mbid=row["mbid"])
        assert str(job.mbid) == row["mbid"]
        assert job.status == "pending"
        assert job.source == row["source"]


def test_can_import_whole_artist(artists, albums, mocker, superuser_client):
    mocker.patch("funkwhale_api.music.tasks.import_job_run")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get", return_value=artists["get"]["soad"]
    )
    mocker.patch("funkwhale_api.musicbrainz.api.images.get_front", return_value=b"")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get_with_includes"]["hypnotize"],
    )
    payload = {
        "artistId": "mbid",
        "albums": [
            {
                "releaseId": "47ae093f-1607-49a3-be11-a15d335ccc94",
                "tracks": [
                    {
                        "mbid": "1968a9d6-8d92-4051-8f76-674e157b6eed",
                        "source": "https://www.youtube.com/watch?v=1111111111",
                    },
                    {
                        "mbid": "2968a9d6-8d92-4051-8f76-674e157b6eed",
                        "source": "https://www.youtube.com/watch?v=2222222222",
                    },
                    {
                        "mbid": "3968a9d6-8d92-4051-8f76-674e157b6eed",
                        "source": "https://www.youtube.com/watch?v=3333333333",
                    },
                ],
            }
        ],
    }
    url = reverse("api:v1:submit-artist")
    response = superuser_client.post(
        url, json.dumps(payload), content_type="application/json"
    )

    batch = models.ImportBatch.objects.latest("id")
    assert batch.jobs.count() == 3
    assert batch.submitted_by == superuser_client.user
    assert batch.status == "pending"

    album = models.Album.objects.latest("id")
    assert str(album.mbid) == "47ae093f-1607-49a3-be11-a15d335ccc94"
    medium_data = albums["get_with_includes"]["hypnotize"]["release"]["medium-list"][0]
    assert int(medium_data["track-count"]) == album.tracks.all().count()

    for track in medium_data["track-list"]:
        instance = models.Track.objects.get(mbid=track["recording"]["id"])
        assert instance.title == track["recording"]["title"]
        assert instance.position == int(track["position"])
        assert instance.title == track["recording"]["title"]

    for row in payload["albums"][0]["tracks"]:
        job = models.ImportJob.objects.get(mbid=row["mbid"])
        assert str(job.mbid) == row["mbid"]
        assert job.status == "pending"
        assert job.source == row["source"]


def test_user_can_create_an_empty_batch(superuser_api_client, factories):
    url = reverse("api:v1:import-batches-list")
    response = superuser_api_client.post(url)

    assert response.status_code == 201

    batch = superuser_api_client.user.imports.latest("id")

    assert batch.submitted_by == superuser_api_client.user
    assert batch.source == "api"


def test_user_can_create_import_job_with_file(superuser_api_client, factories, mocker):
    path = os.path.join(DATA_DIR, "test.ogg")
    m = mocker.patch("funkwhale_api.common.utils.on_commit")
    batch = factories["music.ImportBatch"](submitted_by=superuser_api_client.user)
    url = reverse("api:v1:import-jobs-list")
    with open(path, "rb") as f:
        content = f.read()
        f.seek(0)
        response = superuser_api_client.post(
            url, {"batch": batch.pk, "audio_file": f, "source": "file://"}
        )

    assert response.status_code == 201

    job = batch.jobs.latest("id")

    assert job.status == "pending"
    assert job.source.startswith("file://")
    assert "test.ogg" in job.source
    assert job.audio_file.read() == content

    m.assert_called_once_with(tasks.import_job_run.delay, import_job_id=job.pk)


@pytest.mark.parametrize(
    "route,method",
    [
        ("api:v1:tags-list", "get"),
        ("api:v1:tracks-list", "get"),
        ("api:v1:artists-list", "get"),
        ("api:v1:albums-list", "get"),
    ],
)
def test_can_restrict_api_views_to_authenticated_users(
    db, route, method, preferences, client
):
    url = reverse(route)
    preferences["common__api_authentication_required"] = True
    response = getattr(client, method)(url)
    assert response.status_code == 401


def test_track_file_url_is_restricted_to_authenticated_users(
    api_client, factories, preferences
):
    preferences["common__api_authentication_required"] = True
    f = factories["music.TrackFile"]()
    assert f.audio_file is not None
    url = f.path
    response = api_client.get(url)
    assert response.status_code == 401


def test_track_file_url_is_accessible_to_authenticated_users(
    logged_in_api_client, factories, preferences
):
    preferences["common__api_authentication_required"] = True
    f = factories["music.TrackFile"]()
    assert f.audio_file is not None
    url = f.path
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "/_protected{}".format(f.audio_file.url)
