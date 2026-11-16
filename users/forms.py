from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator

from .models import CustomUser


PIN_VALIDATOR = RegexValidator(
    regex=r"^\d{4}$",
    message="Enter a 4-digit PIN.",
)


class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Phone number",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "tel",
                "autofocus": True,
                "placeholder": "+251...",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        label="4-digit PIN",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "inputmode": "numeric",
                "placeholder": "4-digit PIN",
                "class": "form-control",
            }
        ),
    )


class UserRegisterForm(forms.ModelForm):
    pin1 = forms.CharField(
        label="4-digit PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "inputmode": "numeric",
                "maxlength": "4",
            }
        ),
    )
    pin2 = forms.CharField(
        label="Confirm PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "inputmode": "numeric",
                "maxlength": "4",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "phone_number"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+251 9..."}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"].strip()
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        pin1 = cleaned_data.get("pin1")
        pin2 = cleaned_data.get("pin2")
        if pin1 and pin2 and pin1 != pin2:
            self.add_error("pin2", "The PIN entries do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["pin1"])
        user.onboarding_complete = False
        user.pin_setup_required = False
        if commit:
            user.save()
            self.save_m2m()
        return user


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="4-digit PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"inputmode": "numeric", "maxlength": "4"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"inputmode": "numeric", "maxlength": "4"}
        ),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "phone_number", "groups")

    def clean(self):
        cleaned_data = super().clean()
        pin1 = cleaned_data.get("password1")
        pin2 = cleaned_data.get("password2")
        if pin1 and pin2 and pin1 != pin2:
            self.add_error("password2", "The PIN entries do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()
        return user


class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class ProfileCreateForm(forms.ModelForm):
    pin1 = forms.CharField(
        label="New 4-digit PIN",
        required=False,
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "inputmode": "numeric", "maxlength": "4"}
        ),
    )
    pin2 = forms.CharField(
        label="Confirm new PIN",
        required=False,
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "inputmode": "numeric", "maxlength": "4"}
        ),
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
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
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Tell others about yourself..."}
            ),
            "location": forms.TextInput(attrs={"placeholder": "Your location"}),
            "email": forms.EmailInput(attrs={"placeholder": "your@email.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_picture"].required = False
        self.fields["profile_picture"].validators = [
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
        ]
        self.fields["pin1"].required = self.instance.pin_setup_required
        self.fields["pin2"].required = self.instance.pin_setup_required

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if (
            CustomUser.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        pin1 = cleaned_data.get("pin1")
        pin2 = cleaned_data.get("pin2")
        if self.instance.pin_setup_required and not pin1:
            self.add_error("pin1", "Set a new 4-digit PIN to continue.")
        if pin1 and pin2 and pin1 != pin2:
            self.add_error("pin2", "The PIN entries do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.pin_setup_required:
            user.set_password(self.cleaned_data["pin1"])
            user.pin_setup_required = False
        user.onboarding_complete = True
        if commit:
            user.save()
            self.save_m2m()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "profile_picture",
            "bio",
            "location",
            "telegram",
            "facebook",
            "instagram",
            "linkedin",
            "imo",
            "tiktok",
            "email",
        ]
        widgets = {
            "profile_picture": forms.FileInput(
                attrs={"accept": "image/*", "class": "form-control-file"}
            ),
            "bio": forms.Textarea(attrs={"rows": 3}),
            "location": forms.TextInput(attrs={"placeholder": "Your location"}),
            "telegram": forms.TextInput(attrs={"placeholder": "Telegram username"}),
            "facebook": forms.TextInput(attrs={"placeholder": "Facebook username"}),
            "instagram": forms.TextInput(attrs={"placeholder": "Instagram username"}),
            "linkedin": forms.TextInput(attrs={"placeholder": "LinkedIn username"}),
            "imo": forms.TextInput(attrs={"placeholder": "Imo username"}),
            "tiktok": forms.TextInput(attrs={"placeholder": "TikTok username"}),
            "email": forms.EmailInput(attrs={"placeholder": "your@email.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_picture"].validators = [
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
        ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if (
            CustomUser.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError("This username is already taken.")
        return username


class PinChangeForm(forms.Form):
    current_pin = forms.CharField(
        label="Current PIN",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    new_pin = forms.CharField(
        label="New 4-digit PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "inputmode": "numeric", "maxlength": "4"}
        ),
    )
    confirm_pin = forms.CharField(
        label="Confirm new PIN",
        strip=False,
        validators=[PIN_VALIDATOR],
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "inputmode": "numeric", "maxlength": "4"}
        ),
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_pin(self):
        current_pin = self.cleaned_data["current_pin"]
        if not self.user.check_password(current_pin):
            raise ValidationError("The current PIN is incorrect.")
        return current_pin

    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get("new_pin")
        confirm_pin = cleaned_data.get("confirm_pin")
        if new_pin and confirm_pin and new_pin != confirm_pin:
            self.add_error("confirm_pin", "The PIN entries do not match.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_pin"])
        self.user.save(update_fields=["password"])
