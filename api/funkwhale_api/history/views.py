from rest_framework import mixins, permissions, viewsets

from funkwhale_api.activity import record

from . import models, serializers


class ListeningViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):

    serializer_class = serializers.ListeningSerializer
    queryset = models.Listening.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        r = super().perform_create(serializer)
        record.send(serializer.instance)
        return r

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context
