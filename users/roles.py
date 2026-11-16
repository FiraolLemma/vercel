# project/users/roles.py
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    FARMER = "farmer", "Farmer"
    CUSTOMER = "customer", "Customer"
    SUPPLIER = "supplier", "Supplier"
    VETERINARIAN = "veterinarian", "Veterinarian"
    SERVICE_PROVIDER = "service_provider", "Service Provider"
    AI_VIRTUAL_USER = "ai_virtual_user", "AI Virtual User"


ROLE_GROUP_NAMES = {
    role.value: role.label
    for role in UserRole
}


def role_group_name(role):
    value = str(role).strip()
    for candidate in UserRole:
        if value.casefold() in {
            candidate.value.casefold(),
            candidate.label.casefold(),
        }:
            return ROLE_GROUP_NAMES[candidate.value]
    return None


def has_any_role(user, *roles):
    if not user.is_authenticated or getattr(user, "is_virtual_user", False):
        return False
    return user.is_staff or any(user.has_role(role) for role in roles)


def role_required(*roles):
    def decorate(view):
        @login_required
        @wraps(view)
        def guarded_view(request, *args, **kwargs):
            if has_any_role(request.user, *roles):
                return view(request, *args, **kwargs)
            raise PermissionDenied

        return guarded_view

    return decorate
