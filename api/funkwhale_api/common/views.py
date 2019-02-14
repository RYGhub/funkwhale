class SkipFilterForGetObject:
    def get_object(self, *args, **kwargs):
        setattr(self.request, "_skip_filters", True)
        return super().get_object(*args, **kwargs)

    def filter_queryset(self, queryset):
        if getattr(self.request, "_skip_filters", False):
            return queryset
        return super().filter_queryset(queryset)
