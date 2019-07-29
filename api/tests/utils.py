import datetime
from rest_framework import fields as rest_fields


def to_api_date(value):
    if isinstance(value, datetime.datetime):
        f = rest_fields.DateTimeField()
        return f.to_representation(value)
    if isinstance(value, datetime.date):
        f = rest_fields.DateField()
        return f.to_representation(value)
    raise ValueError("Invalid value: {}".format(value))
