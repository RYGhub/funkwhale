import xml.etree.ElementTree as ET

from rest_framework import renderers


class SubsonicJSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = {"subsonic-response": {"status": "ok", "version": "1.16.0"}}
        final["subsonic-response"].update(data)
        if "error" in final:
            # an error was returned
            final["subsonic-response"]["status"] = "failed"
        return super().render(final, accepted_media_type, renderer_context)


class SubsonicXMLRenderer(renderers.JSONRenderer):
    media_type = "text/xml"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = {
            "xmlns": "http://subsonic.org/restapi",
            "status": "ok",
            "version": "1.16.0",
        }
        final.update(data)
        if "error" in final:
            # an error was returned
            final["status"] = "failed"
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
