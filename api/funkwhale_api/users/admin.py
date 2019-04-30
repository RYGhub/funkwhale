# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from funkwhale_api.common import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from . import models


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = models.User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": "This username has already been taken."}
    )

    class Meta(UserCreationForm.Meta):
        model = models.User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages["duplicate_username"])


def disable(modeladmin, request, queryset):
    queryset.exclude(pk=request.user.pk).update(is_active=False)


disable.short_description = "Disable login"


def enable(modeladmin, request, queryset):
    queryset.update(is_active=True)


enable.short_description = "Enable login"


@admin.register(models.User)
class UserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = [
        "username",
        "email",
        "is_active",
        "date_joined",
        "last_login",
        "is_staff",
        "is_superuser",
    ]
    list_filter = [
        "is_superuser",
        "is_staff",
        "privacy_level",
        "permission_settings",
        "permission_library",
        "permission_moderation",
    ]
    actions = [disable, enable]
    fieldsets = (
        (None, {"fields": ("username", "password", "privacy_level")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "avatar")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "permission_library",
                    "permission_settings",
                    "permission_moderation",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Useless fields"), {"fields": ("user_permissions", "groups")}),
    )


@admin.register(models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ["owner", "code", "creation_date", "expiration_date"]
    search_fields = ["owner__username", "code"]
    readonly_fields = ["expiration_date", "code"]
