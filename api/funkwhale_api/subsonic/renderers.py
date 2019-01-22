import xml.etree.ElementTree as ET

from rest_framework import renderers

import funkwhale_api


def structure_payload(data):
    payload = {
        "status": "ok",
        "version": "1.16.0",
        "type": "funkwhale",
        "funkwhaleVersion": funkwhale_api.__version__,
    }
    payload.update(data)
    if "detail" in payload:
        payload["error"] = {"code": 0, "message": payload.pop("detail")}
    if "error" in payload:
        payload["status"] = "failed"
    return payload


class SubsonicJSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = {"subsonic-response": structure_payload(data)}
        return super().render(final, accepted_media_type, renderer_context)


class SubsonicXMLRenderer(renderers.JSONRenderer):
    media_type = "text/xml"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = structure_payload(data)
        final["xmlns"] = "http://subsonic.org/restapi"
        tree = dict_to_xml_tree("subsonic-response", final)
        return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            tree, encoding="utf-8"
        )


def dict_to_xml_tree(root_tag, d, parent=None):
    root = ET.Element(root_tag)
    for key, value in d.items():
        if isinstance(value, dict):
            root.append(dict_to_xml_tree(key, value, parent=root))
        elif isinstance(value, list):
            for obj in value:
                root.append(dict_to_xml_tree(key, obj, parent=root))
        else:
            root.set(key, str(value))
    return root
