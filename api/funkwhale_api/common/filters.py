from django import forms
from django.db.models import Q

from django_filters import widgets
from django_filters import rest_framework as filters

from . import fields
from . import models
from . import search


class NoneObject(object):
    def __eq__(self, other):
        return other.__class__ == NoneObject


NONE = NoneObject()
NULL_BOOLEAN_CHOICES = [
    (True, True),
    ("true", True),
    ("True", True),
    ("1", True),
    ("yes", True),
    (False, False),
    ("false", False),
    ("False", False),
    ("0", False),
    ("no", False),
    ("None", NONE),
    ("none", NONE),
    ("Null", NONE),
    ("null", NONE),
]


class CoerceChoiceField(forms.ChoiceField):
    """
    Same as forms.ChoiceField but will return the second value
    in the choices tuple instead of the user provided one
    """

    def clean(self, value):
        if value is None:
            return value
        v = super().clean(value)
        try:
            return [b for a, b in self.choices if v == a][0]
        except IndexError:
            raise forms.ValidationError("Invalid value {}".format(value))


class NullBooleanFilter(filters.ChoiceFilter):
    field_class = CoerceChoiceField

    def __init__(self, *args, **kwargs):
        self.choices = NULL_BOOLEAN_CHOICES
        kwargs["choices"] = self.choices
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in ["", None]:
            return qs
        if value == NONE:
            value = None
        qs = self.get_method(qs)(
            **{"%s__%s" % (self.field_name, self.lookup_expr): value}
        )
        return qs.distinct() if self.distinct else qs


def clean_null_boolean_filter(v):
    v = CoerceChoiceField(choices=NULL_BOOLEAN_CHOICES).clean(v)
    if v == NONE:
        v = None

    return v


def get_null_boolean_filter(name):
    return {"handler": lambda v: Q(**{name: clean_null_boolean_filter(v)})}


class DummyTypedMultipleChoiceField(forms.TypedMultipleChoiceField):
    def valid_value(self, value):
        return True


class QueryArrayWidget(widgets.QueryArrayWidget):
    """
    Until https://github.com/carltongibson/django-filter/issues/1047 is fixed
    """

    def value_from_datadict(self, data, files, name):
        data = data.copy()
        return super().value_from_datadict(data, files, name)


class MultipleQueryFilter(filters.TypedMultipleChoiceFilter):
    field_class = DummyTypedMultipleChoiceField

    def __init__(self, *args, **kwargs):
        kwargs["widget"] = QueryArrayWidget()
        super().__init__(*args, **kwargs)
        self.lookup_expr = "in"


def filter_target(value):

    config = {
        "artist": ["artist", "target_id", int],
        "album": ["album", "target_id", int],
        "track": ["track", "target_id", int],
    }
    parts = value.lower().split(" ")
    if parts[0].strip() not in config:
        raise forms.ValidationError("Improper target")

    conf = config[parts[0].strip()]

    query = Q(target_content_type__model=conf[0])
    if len(parts) > 1:
        _, lookup_field, validator = conf
        try:
            lookup_value = validator(parts[1].strip())
        except TypeError:
            raise forms.ValidationError("Imparsable target id")
        return query & Q(**{lookup_field: lookup_value})

    return query


class MutationFilter(filters.FilterSet):
    is_approved = NullBooleanFilter("is_approved")
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "summary": {"to": "summary"},
                "fid": {"to": "fid"},
                "type": {"to": "type"},
            },
            filter_fields={
                "domain": {"to": "created_by__domain__name__iexact"},
                "is_approved": get_null_boolean_filter("is_approved"),
                "target": {"handler": filter_target},
                "is_applied": {"to": "is_applied"},
            },
        )
    )

    class Meta:
        model = models.Mutation
        fields = ["is_approved", "is_applied", "type"]
