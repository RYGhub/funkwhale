from rest_framework import serializers


class ActionSerializer(serializers.Serializer):
    """
    A special serializer that can operate on a list of objects
    and apply actions on it.
    """

    action = serializers.CharField(required=True)
    objects = serializers.JSONField(required=True)
    filters = serializers.DictField(required=False)
    actions = None
    filterset_class = None

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        if self.actions is None:
            raise ValueError(
                'You must declare a list of actions on '
                'the serializer class')

        for action in self.actions:
            handler_name = 'handle_{}'.format(action)
            assert hasattr(self, handler_name), (
                '{} miss a {} method'.format(
                    self.__class__.__name__, handler_name)
            )
        super().__init__(self, *args, **kwargs)

    def validate_action(self, value):
        if value not in self.actions:
            raise serializers.ValidationError(
                '{} is not a valid action. Pick one of {}.'.format(
                    value, ', '.join(self.actions)
                )
            )
        return value

    def validate_objects(self, value):
        qs = None
        if value == 'all':
            return self.queryset.all().order_by('id')
        if type(value) in [list, tuple]:
            return self.queryset.filter(pk__in=value).order_by('id')

        raise serializers.ValidationError(
            '{} is not a valid value for objects. You must provide either a '
            'list of identifiers or the string "all".'.format(value))

    def validate(self, data):
        if not self.filterset_class or 'filters' not in data:
            # no additional filters to apply, we just skip
            return data

        qs_filterset = self.filterset_class(
            data['filters'], queryset=data['objects'])
        try:
            assert qs_filterset.form.is_valid()
        except (AssertionError, TypeError):
            raise serializers.ValidationError('Invalid filters')
        data['objects'] = qs_filterset.qs
        return data

    def save(self):
        handler_name = 'handle_{}'.format(self.validated_data['action'])
        handler = getattr(self, handler_name)
        result = handler(self.validated_data['objects'])
        payload = {
            'updated': self.validated_data['objects'].count(),
            'action': self.validated_data['action'],
            'result': result,
        }
        return payload
