from django.db import transaction

from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import response
from rest_framework import status

from . import filters
from . import models
from . import mutations as common_mutations
from . import serializers
from . import signals
from . import tasks
from . import utils


def action_route(serializer_class):
    @decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializer_class(request.data, queryset=queryset)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)

    return action


def mutations_route(types):
    """
    Given a queryset and a list of mutation types, return a view
    that can be included in any viewset, and serve:

    GET /{id}/mutations/ - list of mutations for the given object
    POST /{id}/mutations/ - create a mutation for the given object
    """

    @transaction.atomic
    def mutations(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.method == "GET":
            queryset = models.Mutation.objects.get_for_target(obj).filter(
                type__in=types
            )
            queryset = queryset.order_by("-creation_date")
            filterset = filters.MutationFilter(request.GET, queryset=queryset)
            page = self.paginate_queryset(filterset.qs)
            if page is not None:
                serializer = serializers.APIMutationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializers.APIMutationSerializer(queryset, many=True)
            return response.Response(serializer.data)
        if request.method == "POST":
            if not request.user.is_authenticated:
                raise exceptions.NotAuthenticated()
            serializer = serializers.APIMutationSerializer(
                data=request.data, context={"registry": common_mutations.registry}
            )
            serializer.is_valid(raise_exception=True)
            if not common_mutations.registry.has_perm(
                actor=request.user.actor,
                type=serializer.validated_data["type"],
                obj=obj,
                perm="approve"
                if serializer.validated_data.get("is_approved", False)
                else "suggest",
            ):
                raise exceptions.PermissionDenied()

            final_payload = common_mutations.registry.get_validated_payload(
                type=serializer.validated_data["type"],
                payload=serializer.validated_data["payload"],
                obj=obj,
            )
            mutation = serializer.save(
                created_by=request.user.actor,
                target=obj,
                payload=final_payload,
                is_approved=serializer.validated_data.get("is_approved", None),
            )
            if mutation.is_approved:
                utils.on_commit(tasks.apply_mutation.delay, mutation_id=mutation.pk)

            utils.on_commit(
                signals.mutation_created.send, sender=None, mutation=mutation
            )
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    return decorators.action(
        methods=["get", "post"], detail=True, required_scope="edits"
    )(mutations)
