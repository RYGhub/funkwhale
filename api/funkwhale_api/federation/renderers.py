from rest_framework.renderers import JSONRenderer


class ActivityPubRenderer(JSONRenderer):
    media_type = 'application/activity+json'


class WebfingerRenderer(JSONRenderer):
    media_type = 'application/jrd+json'
