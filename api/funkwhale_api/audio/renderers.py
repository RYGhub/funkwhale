import xml.etree.ElementTree as ET

from rest_framework import negotiation
from rest_framework import renderers

from funkwhale_api.subsonic.renderers import dict_to_xml_tree


class PodcastRSSRenderer(renderers.JSONRenderer):
    media_type = "application/rss+xml"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = {
            "version": "2.0",
            "xmlns:atom": "http://www.w3.org/2005/Atom",
            "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            "xmlns:media": "http://search.yahoo.com/mrss/",
        }
        final.update(data)
        tree = dict_to_xml_tree("rss", final)
        return render_xml(tree)


class PodcastRSSContentNegociation(negotiation.DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix=None):

        return (PodcastRSSRenderer(), PodcastRSSRenderer.media_type)


def render_xml(tree):
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        tree, encoding="utf-8"
    )
