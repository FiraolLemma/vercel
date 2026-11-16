from django.conf import settings
from django.db import migrations


ROLE_GROUP_NAMES = {
    "admin": "Admin",
    "farmer": "Farmer",
    "customer": "Customer",
    "supplier": "Supplier",
    "veterinarian": "Veterinarian",
    "service_provider": "Service Provider",
    "ai_virtual_user": "AI Virtual User",
}


def create_role_groups_and_assign_users(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    VirtualAgent = apps.get_model("virtual_users", "VirtualAgent")
    database = schema_editor.connection.alias

    groups = {
        role: Group.objects.using(database).get_or_create(name=name)[0]
        for role, name in ROLE_GROUP_NAMES.items()
    }

    recognized_names = list(ROLE_GROUP_NAMES.values())
    users = User.objects.using(database)

    for user in users.filter(is_staff=True) | users.filter(is_superuser=True):
        user.groups.add(groups["admin"])

    virtual_user_ids = VirtualAgent.objects.using(database).values_list(
        "user_id",
        flat=True,
    )
    other_groups = list(
        Group.objects.using(database).filter(
            name__in=[
                name
                for role, name in ROLE_GROUP_NAMES.items()
                if role != "ai_virtual_user"
            ],
        )
    )
    for user in users.filter(pk__in=virtual_user_ids).iterator():
        user.groups.remove(*other_groups)
        user.groups.add(groups["ai_virtual_user"])

    users_without_role = users.exclude(pk__in=virtual_user_ids).exclude(
        groups__name__in=recognized_names,
    ).distinct()
    for user in users_without_role:
        user.groups.add(groups["customer"])


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0001_initial"),
        ("virtual_users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_role_groups_and_assign_users,
            migrations.RunPython.noop,
        ),
    ]
