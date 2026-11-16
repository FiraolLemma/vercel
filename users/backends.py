import re

from django.contrib.auth.backends import ModelBackend

from .models import CustomUser


class UsernamePhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone_number = username or kwargs.get("phone_number")
        password = password or kwargs.get("pin")
        if not phone_number or password is None:
            return None

        try:
            user = CustomUser._default_manager.get_by_natural_key(phone_number)
        except CustomUser.DoesNotExist:
            CustomUser().set_password(password)
            return None

        valid_pin = bool(re.fullmatch(r"\d{4}", password))
        valid_credential = user.check_password(password) and (
            user.pin_setup_required or valid_pin
        )
        if (
            valid_credential
            and self.user_can_authenticate(user)
            and not user.is_virtual_user
        ):
            return user
        return None
