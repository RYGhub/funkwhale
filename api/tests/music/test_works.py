
from funkwhale_api.music import models


def test_can_import_work(factories, mocker, works):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.works.get",
        return_value=works["get"]["chop_suey"],
    )
    recording = factories["music.Track"](mbid="07ca77cf-f513-4e9c-b190-d7e24bbad448")
    mbid = "e2ecabc4-1b9d-30b2-8f30-3596ec423dc5"
    work = models.Work.create_from_api(id=mbid)

    assert work.title == "Chop Suey!"
    assert work.nature == "song"
    assert work.language == "eng"
    assert work.mbid == mbid

    # a imported work should also be linked to corresponding recordings

    recording.refresh_from_db()
    assert recording.work == work


def test_can_get_work_from_recording(factories, mocker, works, tracks):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.works.get",
        return_value=works["get"]["chop_suey"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.get",
        return_value=tracks["get"]["chop_suey"],
    )
    recording = factories["music.Track"](
        work=None, mbid="07ca77cf-f513-4e9c-b190-d7e24bbad448"
    )
    mbid = "e2ecabc4-1b9d-30b2-8f30-3596ec423dc5"

    assert recording.work == None

    work = recording.get_work()

    assert work.title == "Chop Suey!"
    assert work.nature == "song"
    assert work.language == "eng"
    assert work.mbid == mbid

    recording.refresh_from_db()
    assert recording.work == work


def test_works_import_lyrics_if_any(db, mocker, works):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.works.get",
        return_value=works["get"]["chop_suey"],
    )
    mbid = "e2ecabc4-1b9d-30b2-8f30-3596ec423dc5"
    work = models.Work.create_from_api(id=mbid)

    lyrics = models.Lyrics.objects.latest("id")
    assert lyrics.work == work
    assert lyrics.url == "http://lyrics.wikia.com/System_Of_A_Down:Chop_Suey!"
