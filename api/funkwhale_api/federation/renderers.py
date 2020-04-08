from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.renderers import JSONRenderer


def get_ap_renderers():
    MEDIA_TYPES = [
        ("APActivity", "application/activity+json"),
        ("APLD", "application/ld+json"),
        ("APJSON", "application/json"),
        ("HTML", "text/html"),
    ]

    return [
        type(name, (JSONRenderer,), {"media_type": media_type})
        for name, media_type in MEDIA_TYPES
    ]


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    def select_parser(self, request, parsers):
        """
        Select the first parser in the `.parser_classes` list.
        """
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        return (renderers[0], renderers[0].media_type)


class WebfingerRenderer(JSONRenderer):
    media_type = "application/jrd+json"
