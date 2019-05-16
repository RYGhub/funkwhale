from rest_framework.pagination import PageNumberPagination, _positive_int


class FunkwhalePagination(PageNumberPagination):
    page_size_query_param = "page_size"
    default_max_page_size = 50
    default_page_size = None
    view = None

    def paginate_queryset(self, queryset, request, view=None):
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_page_size(self, request):
        max_page_size = (
            getattr(self.view, "max_page_size", 0) or self.default_max_page_size
        )
        page_size = getattr(self.view, "default_page_size", 0) or max_page_size
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=max_page_size,
                )
            except (KeyError, ValueError):
                pass

        return page_size
