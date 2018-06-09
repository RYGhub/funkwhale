from rest_framework import parsers


class ActivityParser(parsers.JSONParser):
    media_type = "application/activity+json"
