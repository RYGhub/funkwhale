import json
import xml.etree.ElementTree as ET

from funkwhale_api.subsonic import renderers


def test_json_renderer():
    data = {"hello": "world"}
    expected = {
        "subsonic-response": {"status": "ok", "version": "1.16.0", "hello": "world"}
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
    expected = b'<?xml version="1.0" encoding="UTF-8"?>\n<subsonic-response hello="world" status="ok" version="1.16.0" xmlns="http://subsonic.org/restapi" />'  # noqa

    renderer = renderers.SubsonicXMLRenderer()
    rendered = renderer.render(payload)

    assert rendered == expected
