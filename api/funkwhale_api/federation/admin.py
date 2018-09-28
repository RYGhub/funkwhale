from django.contrib import admin

from . import models
from . import tasks


def redeliver_deliveries(modeladmin, request, queryset):
    queryset.update(is_delivered=False)
    for delivery in queryset:
        tasks.deliver_to_remote.delay(delivery_id=delivery.pk)


redeliver_deliveries.short_description = "Redeliver"


def redeliver_activities(modeladmin, request, queryset):
    for activity in queryset.select_related("actor__user"):
        if activity.actor.get_user():
            tasks.dispatch_outbox.delay(activity_id=activity.pk)
        else:
            tasks.dispatch_inbox.delay(activity_id=activity.pk)


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
    list_display = ["actor", "activity", "type", "is_read"]
    list_filter = ["type", "activity__type", "is_read"]
    search_fields = ["actor__fid", "activity__fid"]
    list_select_related = True


@admin.register(models.Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        "inbox_url",
        "activity",
        "last_attempt_date",
        "attempts",
        "is_delivered",
    ]
    list_filter = ["activity__type", "is_delivered"]
    search_fields = ["inbox_url"]
    list_select_related = True
    actions = [redeliver_deliveries]
