import re

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .roles import ROLE_GROUP_NAMES, UserRole, role_group_name


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        if not phone_number:
            raise ValueError("Phone number must be set")

        user = self.model(
            username=username,
            phone_number=phone_number,
            **extra_fields,
        )
        if password:
            user.set_password(password)
            if not re.fullmatch(r"\d{4}", password):
                user.pin_setup_required = True
                user.onboarding_complete = False
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("onboarding_complete", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if not password:
            raise ValueError("Superuser must have a password.")

        if len(password) != 4 or not password.isdigit():
            extra_fields["pin_setup_required"] = True
            extra_fields["onboarding_complete"] = False

        return self.create_user(
            username,
            phone_number,
            password=password,
            **extra_fields,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be in format: '+999999999'",
            )
        ],
    )
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pics/default.jpg",
        blank=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    imo = models.CharField(max_length=100, blank=True, null=True)
    tiktok = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    onboarding_complete = models.BooleanField(default=True)
    pin_setup_required = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.phone_number})"

    @property
    def profile(self):
        return self

    def has_role(self, role):
        group_name = role_group_name(role)
        if (
            group_name == role_group_name(UserRole.ADMIN)
            and (self.is_staff or self.is_superuser)
        ):
            return True
        return bool(
            group_name
            and self.is_authenticated
            and self.groups.filter(name=group_name).exists()
        )

    @property
    def is_virtual_user(self):
        return bool(
            self.pk
            and type(self).objects.filter(
                pk=self.pk,
                virtual_agent__isnull=False,
            ).exists()
        )

    @property
    def role_labels(self):
        if not self.pk:
            return ()
        labels = set(
            self.groups.filter(name__in=ROLE_GROUP_NAMES.values())
            .values_list("name", flat=True)
        )
        if self.is_staff or self.is_superuser:
            labels.add(UserRole.ADMIN.label)
        if self.is_virtual_user:
            labels.add(UserRole.AI_VIRTUAL_USER.label)
        return tuple(
            role.label
            for role in UserRole
            if role.label in labels
        )

    def get_unread_message_count(self):
        if not self.is_authenticated:
            return 0

        from conversation.models import ConversationMessage

        return ConversationMessage.objects.filter(
            conversation__members=self,
            is_read=False,
        ).exclude(created_by=self).count()
