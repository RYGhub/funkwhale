from django.contrib import admin

from . import models
from . import tasks


def redeliver_inbox_items(modeladmin, request, queryset):
    for id in set(
        queryset.filter(activity__actor__user__isnull=False).values_list(
            "activity", flat=True
        )
    ):
        tasks.dispatch_outbox.delay(activity_id=id)


redeliver_inbox_items.short_description = "Redeliver"


def redeliver_activities(modeladmin, request, queryset):
    for id in set(
        queryset.filter(actor__user__isnull=False).values_list("id", flat=True)
    ):
        tasks.dispatch_outbox.delay(activity_id=id)


redeliver_activities.short_description = "Redeliver"


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["type", "fid", "url", "actor", "creation_date"]
    search_fields = ["payload", "fid", "url", "actor__domain"]
    list_filter = ["type", "actor__domain"]
    actions = [redeliver_activities]
    list_select_related = True


@admin.register(models.Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = [
        "fid",
        "domain",
        "preferred_username",
        "type",
        "creation_date",
        "last_fetch_date",
    ]
    search_fields = ["fid", "domain", "preferred_username"]
    list_filter = ["type"]


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["actor", "target", "approved", "creation_date"]
    list_filter = ["approved"]
    search_fields = ["actor__fid", "target__fid"]
    list_select_related = True


@admin.register(models.LibraryFollow)
class LibraryFollowAdmin(admin.ModelAdmin):
    list_display = ["actor", "target", "approved", "creation_date"]
    list_filter = ["approved"]
    search_fields = ["actor__fid", "target__fid"]
    list_select_related = True


@admin.register(models.InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = [
        "actor",
        "activity",
        "type",
        "last_delivery_date",
        "delivery_attempts",
    ]
    list_filter = ["type"]
    search_fields = ["actor__fid", "activity__fid"]
    list_select_related = True
    actions = [redeliver_inbox_items]
