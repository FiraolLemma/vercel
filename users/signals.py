
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import CustomUser
from .roles import UserRole, role_group_name


@receiver(post_migrate, dispatch_uid="users.ensure_role_groups")
def ensure_role_groups(sender, **kwargs):
    if sender.label != "users":
        return

    for role in UserRole:
        Group.objects.get_or_create(name=role_group_name(role))


@receiver(post_save, sender=CustomUser)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Automatically assign a default role to newly created users.
    """
    if created:
        role = (
            UserRole.ADMIN
            if instance.is_staff or instance.is_superuser
            else UserRole.CUSTOMER
        )

        group_name = role_group_name(role)

        if group_name:
            group, _ = Group.objects.get_or_create(
                name=group_name
            )
            instance.groups.add(group)


@receiver(post_save, sender="virtual_users.VirtualAgent")
def assign_ai_virtual_role(sender, instance, **kwargs):
    """
    Assign AI virtual users their dedicated role.
    """
    ai_group_name = role_group_name(UserRole.AI_VIRTUAL_USER)

    ai_group, _ = Group.objects.get_or_create(
        name=ai_group_name
    )

    other_role_groups = Group.objects.filter(
        name__in=[
            role_group_name(role)
            for role in UserRole
            if role != UserRole.AI_VIRTUAL_USER
        ]
    )

    instance.user.groups.remove(*other_role_groups)
    instance.user.groups.add(ai_group)
