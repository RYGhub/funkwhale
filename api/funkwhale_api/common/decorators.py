from rest_framework import response
from rest_framework import decorators


def action_route(serializer_class):
    @decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializer_class(request.data, queryset=queryset)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)

    return action
