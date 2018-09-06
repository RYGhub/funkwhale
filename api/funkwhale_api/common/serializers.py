import collections

from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _


class RelatedField(serializers.RelatedField):
    default_error_messages = {
        "does_not_exist": _("Object with {related_field_name}={value} does not exist."),
        "invalid": _("Invalid value."),
    }

    def __init__(self, related_field_name, serializer, **kwargs):
        self.related_field_name = related_field_name
        self.serializer = serializer
        self.filters = kwargs.pop("filters", None)
        kwargs["queryset"] = kwargs.pop(
            "queryset", self.serializer.Meta.model.objects.all()
        )
        super().__init__(**kwargs)

    def get_filters(self, data):
        filters = {self.related_field_name: data}
        if self.filters:
            filters.update(self.filters(self.context))
        return filters

    def to_internal_value(self, data):
        try:
            queryset = self.get_queryset()
            filters = self.get_filters(data)
            return queryset.get(**filters)
        except ObjectDoesNotExist:
            self.fail(
                "does_not_exist",
                related_field_name=self.related_field_name,
                value=smart_text(data),
            )
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return self.serializer.to_representation(obj)

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return collections.OrderedDict(
            [
                (
                    self.to_representation(item)[self.related_field_name],
                    self.display_value(item),
                )
                for item in queryset
            ]
        )


class Action(object):
    def __init__(self, name, allow_all=False, qs_filter=None):
        self.name = name
        self.allow_all = allow_all
        self.qs_filter = qs_filter

    def __repr__(self):
        return "<Action {}>".format(self.name)


class ActionSerializer(serializers.Serializer):
    """
    A special serializer that can operate on a list of objects
    and apply actions on it.
    """

    action = serializers.CharField(required=True)
    objects = serializers.JSONField(required=True)
    filters = serializers.DictField(required=False)
    actions = None
    pk_field = "pk"

    def __init__(self, *args, **kwargs):
        self.actions_by_name = {a.name: a for a in self.actions}
        self.queryset = kwargs.pop("queryset")
        if self.actions is None:
            raise ValueError(
                "You must declare a list of actions on " "the serializer class"
            )

        for action in self.actions_by_name.keys():
            handler_name = "handle_{}".format(action)
            assert hasattr(self, handler_name), "{} miss a {} method".format(
                self.__class__.__name__, handler_name
            )
        super().__init__(self, *args, **kwargs)

    def validate_action(self, value):
        try:
            return self.actions_by_name[value]
        except KeyError:
            raise serializers.ValidationError(
                "{} is not a valid action. Pick one of {}.".format(
                    value, ", ".join(self.actions_by_name.keys())
                )
            )

    def validate_objects(self, value):
        if value == "all":
            return self.queryset.all().order_by("id")
        if type(value) in [list, tuple]:
            return self.queryset.filter(
                **{"{}__in".format(self.pk_field): value}
            ).order_by("id")

        raise serializers.ValidationError(
            "{} is not a valid value for objects. You must provide either a "
            'list of identifiers or the string "all".'.format(value)
        )

    def validate(self, data):
        allow_all = data["action"].allow_all
        if not allow_all and self.initial_data["objects"] == "all":
            raise serializers.ValidationError(
                "You cannot apply this action on all objects"
            )
        final_filters = data.get("filters", {}) or {}
        if self.filterset_class and final_filters:
            qs_filterset = self.filterset_class(final_filters, queryset=data["objects"])
            try:
                assert qs_filterset.form.is_valid()
            except (AssertionError, TypeError):
                raise serializers.ValidationError("Invalid filters")
            data["objects"] = qs_filterset.qs

        if data["action"].qs_filter:
            data["objects"] = data["action"].qs_filter(data["objects"])

        data["count"] = data["objects"].count()
        if data["count"] < 1:
            raise serializers.ValidationError("No object matching your request")
        return data

    def save(self):
        handler_name = "handle_{}".format(self.validated_data["action"].name)
        handler = getattr(self, handler_name)
        result = handler(self.validated_data["objects"])
        payload = {
            "updated": self.validated_data["count"],
            "action": self.validated_data["action"].name,
            "result": result,
        }
        return payload
