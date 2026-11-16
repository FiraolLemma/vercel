from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    list_display = (
        "username",
        "phone_number",
        "role_summary",
        "onboarding_complete",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "onboarding_complete",
        "groups",
    )
    search_fields = ("username", "phone_number", "email")
    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ("last_login",)
    fieldsets = (
        (None, {"fields": ("username", "phone_number", "password")}),
        (
            "Profile",
            {
                "fields": (
                    "profile_picture",
                    "bio",
                    "location",
                    "email",
                    "telegram",
                    "facebook",
                    "instagram",
                    "linkedin",
                    "imo",
                    "tiktok",
                )
            },
        ),
        ("Roles", {"fields": ("groups",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                )
            },
        ),
        ("Account activity", {"fields": ("last_login", "onboarding_complete")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                    "groups",
                ),
            },
        ),
    )

    @admin.display(description="Roles")
    def role_summary(self, user):
        return ", ".join(user.role_labels) or "—"
