from django.contrib import admin

from .models import Company, Farm


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location", "is_verified", "created_at")
    list_filter = ("is_verified", "location")
    search_fields = ("name", "owner__username", "owner__phone_number", "email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "company", "city", "region")
    list_filter = ("region", "country")
    search_fields = ("name", "owner__username", "owner__phone_number", "company__name")
    readonly_fields = ("created_at", "updated_at")
