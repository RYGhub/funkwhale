from django.db import IntegrityError

from rest_framework import mixins
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets

from . import models
from . import serializers


class UserFilterViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        models.UserFilter.objects.all()
        .order_by("-creation_date")
        .select_related("target_artist")
    )
    serializer_class = serializers.UserFilterSerializer
    required_scope = "filters"
    ordering_fields = ("creation_date",)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            content = {"detail": "A content filter already exists for this object"}
            return response.Response(content, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReportsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    lookup_field = "uuid"
    queryset = models.Report.objects.all().order_by("-creation_date")
    serializer_class = serializers.ReportSerializer
    required_scope = "reports"
    ordering_fields = ("creation_date",)
    anonymous_policy = "setting"
    anonymous_scopes = {"write:reports"}
    throttling_scopes = {
        "create": {
            "anonymous": "anonymous-reports",
            "authenticated": "authenticated-reports",
        }
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["submitter"] = self.request.user.actor
        return context

    def perform_create(self, serializer):
        submitter = None
        if self.request.user.is_authenticated:
            submitter = self.request.user.actor
        serializer.save(submitter=submitter)
