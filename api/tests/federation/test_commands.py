from django.core.management import call_command

from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation.management.commands import fix_federation_ids
from funkwhale_api.music import models as music_models


def test_fix_fids_dry_run(factories, mocker):
    replace_prefix = mocker.patch("funkwhale_api.common.utils.replace_prefix")

    call_command("fix_federation_ids", "http://old/", "https://new/", interactive=False)

    replace_prefix.assert_not_called()


def test_fix_fids_no_dry_run(factories, mocker, queryset_equal_queries):
    replace_prefix = mocker.patch("funkwhale_api.common.utils.replace_prefix")
    factories["federation.Actor"](fid="http://old/test")
    call_command(
        "fix_federation_ids",
        "http://old",
        "https://new",
        interactive=False,
        dry_run=False,
    )

    models = [
        (music_models.Artist, ["fid"]),
        (music_models.Album, ["fid"]),
        (music_models.Track, ["fid"]),
        (music_models.Upload, ["fid"]),
        (music_models.Library, ["fid", "followers_url"]),
        (
            federation_models.Actor,
            [
                "fid",
                "url",
                "outbox_url",
                "inbox_url",
                "following_url",
                "followers_url",
                "shared_inbox_url",
            ],
        ),
        (federation_models.Activity, ["fid"]),
        (federation_models.Follow, ["fid"]),
        (federation_models.LibraryFollow, ["fid"]),
    ]
    assert models == fix_federation_ids.MODELS

    for kls, fields in models:
        for field in fields:
            replace_prefix.assert_any_call(
                kls.objects.all(), field, old="http://old", new="https://new"
            )
