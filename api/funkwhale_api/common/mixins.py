from rest_framework import serializers

from django.db.models import Q
from django.shortcuts import get_object_or_404


class MultipleLookupDetailMixin(object):
    lookup_value_regex = "[^/]+"
    lookup_field = "composite"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        relevant_lookup = None
        value = None
        for lookup in self.url_lookups:
            field_validator = lookup["validator"]
            try:
                value = field_validator(self.kwargs["composite"])
            except serializers.ValidationError:
                continue
            else:
                relevant_lookup = lookup
                break
        get_query = relevant_lookup.get(
            "get_query", lambda value: Q(**{relevant_lookup["lookup_field"]: value})
        )
        query = get_query(value)
        obj = get_object_or_404(queryset, query)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
