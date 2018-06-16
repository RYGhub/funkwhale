from rest_framework import mixins, viewsets

from . import filters, models, serializers


class ImportRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = serializers.ImportRequestSerializer
    queryset = (
        models.ImportRequest.objects.all().select_related().order_by("-creation_date")
    )
    filter_class = filters.ImportRequestFilter
    ordering_fields = ("id", "artist_name", "creation_date", "status")

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["user"] = self.request.user
        return context
