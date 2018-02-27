from rest_framework import views
from rest_framework.response import Response

from dynamic_preferences.api import serializers
from dynamic_preferences.registries import global_preferences_registry

from . import stats


class InstanceSettings(views.APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        manager = global_preferences_registry.manager()
        manager.all()
        all_preferences = manager.model.objects.all().order_by(
            'section', 'name'
        )
        api_preferences = [
            p
            for p in all_preferences
            if getattr(p.preference, 'show_in_api', False)
        ]
        data = serializers.GlobalPreferenceSerializer(
            api_preferences, many=True).data
        return Response(data, status=200)


class InstanceStats(views.APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        data = stats.get()
        return Response(data, status=200)
