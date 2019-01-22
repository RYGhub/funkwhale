import json
import os
import pytest

from funkwhale_api.music import models
from funkwhale_api.music import licenses


@pytest.fixture
def purge_license_cache():
    licenses._cache = None
    yield
    licenses._cache = None


def test_licenses_do_not_change():
    """
    We have 100s of licenses static data, and we want to ensure
    that this data do not change without notice.
    So we generate a json file based on this data,
    and ensure our python data match our JSON file.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "licenses.json")
    from_python = licenses.LICENSES
    if os.path.exists(path):
        with open(path) as f:
            from_file = json.loads(f.read())
        assert from_file == from_python
    else:
        # we write the file
        with open(path, "w") as f:
            f.write(json.dumps(from_python, indent=4))


def test_load_licenses_create(db):
    license_data = {
        "code": "dummy",
        "url": "http://dummy",
        "redistribute": True,
        "derivative": True,
        "commercial": True,
        "attribution": True,
        "copyleft": True,
    }
    licenses.load([license_data])

    license = models.License.objects.get(pk=license_data["code"])

    assert license.url == license_data["url"]
    assert license.redistribute == license_data["redistribute"]
    assert license.derivative == license_data["derivative"]
    assert license.copyleft == license_data["copyleft"]
    assert license.commercial == license_data["commercial"]
    assert license.attribution == license_data["attribution"]


def test_load_hardcoded_licenses_works(db):
    licenses.load(licenses.LICENSES)


def test_license_data():
    for data in licenses.LICENSES:
        assert data["identifiers"][0].startswith("http") is True
        required_fields = [
            "code",
            "name",
            "url",
            "derivative",
            "commercial",
            "redistribute",
            "attribution",
        ]
        for field in required_fields:
            assert field in required_fields


def test_load_licenses_update(factories):
    license = models.License.objects.create(
        code="dummy",
        url="http://oldurl",
        redistribute=True,
        derivative=True,
        commercial=True,
        attribution=True,
        copyleft=True,
    )
    license_data = {
        "code": "dummy",
        "url": "http://newurl",
        "redistribute": False,
        "derivative": False,
        "commercial": True,
        "attribution": True,
        "copyleft": True,
    }
    licenses.load([license_data])

    license.refresh_from_db()

    assert license.url == license_data["url"]
    assert license.derivative == license_data["derivative"]
    assert license.copyleft == license_data["copyleft"]
    assert license.commercial == license_data["commercial"]
    assert license.attribution == license_data["attribution"]


def test_load_skip_update_if_no_change(factories, mocker):
    license = models.License.objects.create(
        code="dummy",
        url="http://oldurl",
        redistribute=True,
        derivative=True,
        commercial=True,
        attribution=True,
        copyleft=True,
    )
    update_or_create = mocker.patch.object(models.License.objects, "update_or_create")
    save = mocker.patch.object(models.License, "save")

    # we load licenses but with same data
    licenses.load(
        [
            {
                "code": "dummy",
                "url": license.url,
                "derivative": license.derivative,
                "redistribute": license.redistribute,
                "commercial": license.commercial,
                "attribution": license.attribution,
                "copyleft": license.copyleft,
            }
        ]
    )

    save.assert_not_called()
    update_or_create.assert_not_called()


@pytest.mark.parametrize(
    "value, expected",
    [
        (["http://creativecommons.org/licenses/by-sa/4.0/"], "cc-by-sa-4.0"),
        (["https://creativecommons.org/licenses/by-sa/4.0/"], "cc-by-sa-4.0"),
        (["https://creativecommons.org/licenses/by-sa/4.0"], "cc-by-sa-4.0"),
        (
            [
                "License for this work is: http://creativecommons.org/licenses/by-sa/4.0/"
            ],
            "cc-by-sa-4.0",
        ),
        (
            [
                "License: http://creativecommons.org/licenses/by-sa/4.0/ not http://creativecommons.org/publicdomain/zero/1.0/"  # noqa
            ],
            "cc-by-sa-4.0",
        ),
        (
            [None, "Copyright 2018 http://creativecommons.org/licenses/by-sa/4.0/"],
            "cc-by-sa-4.0",
        ),
        (
            [
                "Unknown",
                "Copyright 2018 http://creativecommons.org/licenses/by-sa/4.0/",
            ],
            "cc-by-sa-4.0",
        ),
        (["Unknown"], None),
        ([""], None),
    ],
)
def test_match(value, expected, db, mocker, purge_license_cache):
    load = mocker.spy(licenses, "load")
    result = licenses.match(*value)

    if expected:
        assert result == models.License.objects.get(code=expected)
        load.assert_called_once_with(licenses.LICENSES)
    else:
        assert result is None


def test_match_cache(mocker, db, purge_license_cache):
    assert licenses._cache is None
    licenses.match("http://test.com")

    assert licenses._cache == sorted(models.License.objects.all(), key=lambda o: o.code)

    load = mocker.patch.object(licenses, "load")
    assert licenses.match(
        "http://creativecommons.org/licenses/by-sa/4.0/"
    ) == models.License.objects.get(code="cc-by-sa-4.0")
    load.assert_not_called()
