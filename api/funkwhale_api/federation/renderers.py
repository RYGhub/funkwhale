from rest_framework.renderers import JSONRenderer


def get_ap_renderers():
    MEDIA_TYPES = [
        ("APActivity", "application/activity+json"),
        ("APLD", "application/ld+json"),
        ("APJSON", "application/json"),
    ]

    return [
        type(name, (JSONRenderer,), {"media_type": media_type})
        for name, media_type in MEDIA_TYPES
    ]


class WebfingerRenderer(JSONRenderer):
    media_type = "application/jrd+json"
