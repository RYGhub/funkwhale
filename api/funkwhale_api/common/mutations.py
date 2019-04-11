import persisting_theory

from rest_framework import serializers

from django.db import models, transaction


class ConfNotFound(KeyError):
    pass


class Registry(persisting_theory.Registry):
    look_into = "mutations"

    def connect(self, type, klass, perm_checkers=None):
        def decorator(serializer_class):
            t = self.setdefault(type, {})
            t[klass] = {
                "serializer_class": serializer_class,
                "perm_checkers": perm_checkers or {},
            }
            return serializer_class

        return decorator

    @transaction.atomic
    def apply(self, type, obj, payload):
        conf = self.get_conf(type, obj)
        serializer = conf["serializer_class"](obj, data=payload)
        serializer.is_valid(raise_exception=True)
        previous_state = serializer.get_previous_state(obj, serializer.validated_data)
        serializer.apply(obj, serializer.validated_data)
        return previous_state

    def is_valid(self, type, obj, payload):
        conf = self.get_conf(type, obj)
        serializer = conf["serializer_class"](obj, data=payload)
        return serializer.is_valid(raise_exception=True)

    def get_validated_payload(self, type, obj, payload):
        conf = self.get_conf(type, obj)
        serializer = conf["serializer_class"](obj, data=payload)
        serializer.is_valid(raise_exception=True)
        return serializer.payload_serialize(serializer.validated_data)

    def has_perm(self, perm, type, obj, actor):
        if perm not in ["approve", "suggest"]:
            raise ValueError("Invalid permission {}".format(perm))
        conf = self.get_conf(type, obj)
        checker = conf["perm_checkers"].get(perm)
        if not checker:
            return False
        return checker(obj=obj, actor=actor)

    def get_conf(self, type, obj):
        try:
            type_conf = self[type]
        except KeyError:
            raise ConfNotFound("{} is not a registered mutation".format(type))

        try:
            conf = type_conf[obj.__class__]
        except KeyError:
            try:
                conf = type_conf[None]
            except KeyError:
                raise ConfNotFound(
                    "No mutation configuration found for {}".format(obj.__class__)
                )
        return conf


class MutationSerializer(serializers.Serializer):
    def apply(self, obj, validated_data):
        raise NotImplementedError()

    def post_apply(self, obj, validated_data):
        pass

    def get_previous_state(self, obj, validated_data):
        return

    def payload_serialize(self, data):
        return data


class UpdateMutationSerializer(serializers.ModelSerializer, MutationSerializer):
    serialized_relations = {}

    def __init__(self, *args, **kwargs):
        # we force partial mode, because update mutations are partial
        kwargs.setdefault("partial", True)
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def apply(self, obj, validated_data):
        r = self.update(obj, validated_data)
        self.post_apply(r, validated_data)
        return r

    def validate(self, validated_data):
        if not validated_data:
            raise serializers.ValidationError("You must update at least one field")

        return super().validate(validated_data)

    def db_serialize(self, validated_data):
        data = {}
        # ensure model fields are serialized properly
        for key, value in list(validated_data.items()):
            if not isinstance(value, models.Model):
                data[key] = value
                continue
            field = self.serialized_relations[key]
            data[key] = getattr(value, field)
        return data

    def payload_serialize(self, data):
        data = super().payload_serialize(data)
        # we use our serialized_relations configuration
        # to ensure we store ids instead of model instances in our json
        # payload
        for field, attr in self.serialized_relations.items():
            try:
                obj = data[field]
            except KeyError:
                continue
            if obj is None:
                data[field] = None
            else:
                data[field] = getattr(obj, attr)
        return data

    def create(self, validated_data):
        validated_data = self.db_serialize(validated_data)
        return super().create(validated_data)

    def get_previous_state(self, obj, validated_data):
        return get_update_previous_state(
            obj,
            *list(validated_data.keys()),
            serialized_relations=self.serialized_relations
        )


def get_update_previous_state(obj, *fields, serialized_relations={}):
    if not fields:
        raise ValueError("You need to provide at least one field")

    state = {}
    for field in fields:
        value = getattr(obj, field)
        if isinstance(value, models.Model):
            # we store the related object id and repr for better UX
            id_field = serialized_relations[field]
            related_value = getattr(value, id_field)
            state[field] = {"value": related_value, "repr": str(value)}
        else:
            state[field] = {"value": value}

    return state


registry = Registry()
