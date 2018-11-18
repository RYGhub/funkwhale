import json
import pytest
import xml.etree.ElementTree as ET

import funkwhale_api

from funkwhale_api.subsonic import renderers


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"hello": "world"},
            {
                "status": "ok",
                "version": "1.16.0",
                "type": "funkwhale",
                "funkwhaleVersion": funkwhale_api.__version__,
                "hello": "world",
            },
        ),
        (
            {
                "hello": "world",
                "error": {"code": 10, "message": "something went wrong"},
            },
            {
                "status": "failed",
                "version": "1.16.0",
                "type": "funkwhale",
                "funkwhaleVersion": funkwhale_api.__version__,
                "hello": "world",
                "error": {"code": 10, "message": "something went wrong"},
            },
        ),
        (
            {"hello": "world", "detail": "something went wrong"},
            {
                "status": "failed",
                "version": "1.16.0",
                "type": "funkwhale",
                "funkwhaleVersion": funkwhale_api.__version__,
                "hello": "world",
                "error": {"code": 0, "message": "something went wrong"},
            },
        ),
    ],
)
def test_structure_payload(data, expected):
    assert renderers.structure_payload(data) == expected


def test_json_renderer():
    data = {"hello": "world"}
    expected = {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.0",
            "type": "funkwhale",
            "funkwhaleVersion": funkwhale_api.__version__,
            "hello": "world",
        }
    }
    renderer = renderers.SubsonicJSONRenderer()
    assert json.loads(renderer.render(data)) == expected


def test_xml_renderer_dict_to_xml():
    payload = {"hello": "world", "item": [{"this": 1}, {"some": "node"}]}
    expected = """<?xml version="1.0" encoding="UTF-8"?>
<key hello="world"><item this="1" /><item some="node" /></key>"""
    result = renderers.dict_to_xml_tree("key", payload)
    exp = ET.fromstring(expected)
    assert ET.tostring(result) == ET.tostring(exp)


def test_xml_renderer():
    payload = {"hello": "world"}
    expected = '<?xml version="1.0" encoding="UTF-8"?>\n<subsonic-response funkwhaleVersion="{}" hello="world" status="ok" type="funkwhale" version="1.16.0" xmlns="http://subsonic.org/restapi" />'  # noqa
    expected = expected.format(funkwhale_api.__version__).encode()

    renderer = renderers.SubsonicXMLRenderer()
    rendered = renderer.render(payload)

    assert rendered == expected
