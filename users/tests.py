from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from virtual_users.models import VirtualAgent

from .roles import UserRole, has_any_role, role_group_name


class AccountAuthenticationTests(TestCase):
    pin = "4826"

    def make_user(self, username="account-user", phone_number="+251911111124"):
        return get_user_model().objects.create_user(
            username=username,
            phone_number=phone_number,
            password=self.pin,
        )

    def test_registration_creates_hashed_pin_and_starts_onboarding(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "new-farmer",
                "phone_number": "+251911111125",
                "pin1": self.pin,
                "pin2": self.pin,
            },
        )

        self.assertRedirects(
            response,
            reverse("users:profile_create"),
            fetch_redirect_response=False,
        )
        user = get_user_model().objects.get(phone_number="+251911111125")
        self.assertTrue(user.check_password(self.pin))
        self.assertFalse(user.onboarding_complete)
        self.assertFalse(user.pin_setup_required)
        self.assertTrue(user.has_role("customer"))

    def test_registration_requires_a_matching_four_digit_pin(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "invalid-pin-user",
                "phone_number": "+251911111126",
                "pin1": "123",
                "pin2": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="invalid-pin-user").exists()
        )

    def test_login_accepts_only_the_four_digit_pin_for_configured_accounts(self):
        user = self.make_user()

        response = self.client.post(
            reverse("users:login"),
            {"username": user.phone_number, "password": "Wrong-123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

        response = self.client.post(
            reverse("users:login"),
            {"username": user.phone_number, "password": self.pin},
        )
        self.assertRedirects(
            response,
            reverse("users:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertIn("_auth_user_id", self.client.session)

        self.client.logout()
        user.is_active = False
        user.save(update_fields=("is_active",))
        self.client.post(
            reverse("users:login"),
            {"username": user.phone_number, "password": self.pin},
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_legacy_credentials_can_only_be_used_to_set_a_pin(self):
        legacy_password = "Legacy-Password-123!"
        user = get_user_model().objects.create_user(
            username="legacy-account",
            phone_number="+251911111127",
            password=legacy_password,
        )
        self.assertTrue(user.pin_setup_required)

        self.client.post(
            reverse("users:login"),
            {"username": user.phone_number, "password": legacy_password},
        )
        response = self.client.get(reverse("users:dashboard"))
        self.assertRedirects(response, reverse("users:profile_create"))

        response = self.client.post(
            reverse("users:profile_create"),
            {
                "username": user.username,
                "pin1": self.pin,
                "pin2": self.pin,
                "bio": "Smallholder farmer",
                "location": "Bishoftu",
                "email": "farmer@example.com",
            },
        )
        self.assertRedirects(response, reverse("users:dashboard"))
        user.refresh_from_db()
        self.assertFalse(user.pin_setup_required)
        self.assertTrue(user.onboarding_complete)
        self.assertEqual(user.bio, "Smallholder farmer")

        self.client.logout()
        self.assertEqual(
            self.client.post(
                reverse("users:login"),
                {"username": user.phone_number, "password": self.pin},
            ).status_code,
            302,
        )
        self.client.logout()
        self.assertEqual(
            self.client.post(
                reverse("users:login"),
                {"username": user.phone_number, "password": legacy_password},
            ).status_code,
            200,
        )

    def test_onboarding_blocks_access_until_profile_is_saved(self):
        self.client.post(
            reverse("users:register"),
            {
                "username": "onboarding-user",
                "phone_number": "+251911111128",
                "pin1": self.pin,
                "pin2": self.pin,
            },
        )
        response = self.client.get(reverse("users:profile"))
        self.assertRedirects(response, reverse("users:profile_create"))

        response = self.client.post(
            reverse("users:profile_create"),
            {
                "username": "onboarding-user",
                "bio": "Growing poultry and crops",
                "location": "Adama",
            },
        )
        self.assertRedirects(response, reverse("users:dashboard"))
        self.assertTrue(
            get_user_model().objects.get(username="onboarding-user").onboarding_complete
        )

    def test_virtual_agent_is_not_allowed_to_log_in(self):
        user = self.make_user(username="virtual-account")
        VirtualAgent.objects.create(
            user=user,
            role=VirtualAgent.Role.FARMER,
            persona_label="Virtual farmer",
        )

        self.assertTrue(user.has_role("ai_virtual_user"))
        self.assertFalse(user.has_role("customer"))
        self.client.post(
            reverse("users:login"),
            {"username": user.phone_number, "password": self.pin},
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_role_groups_exist_and_new_users_default_to_customer(self):
        self.assertEqual(
            set(Group.objects.values_list("name", flat=True)),
            {
                "Admin",
                "Farmer",
                "Customer",
                "Supplier",
                "Veterinarian",
                "Service Provider",
                "AI Virtual User",
            },
        )
        self.assertTrue(self.make_user().has_role("customer"))

    def test_role_group_name_accepts_role_enums_values_and_labels(self):
        for role in UserRole:
            with self.subTest(role=role):
                self.assertEqual(role_group_name(role), role.label)
                self.assertEqual(role_group_name(role.value), role.label)
                self.assertEqual(role_group_name(role.label), role.label)

        self.assertIsNone(role_group_name("unknown"))

        farmer = self.make_user(username="role-name-farmer")
        farmer.groups.remove(Group.objects.get(name="Customer"))
        farmer.groups.add(Group.objects.get(name="Farmer"))
        for role in (UserRole.FARMER, UserRole.FARMER.value, UserRole.FARMER.label):
            with self.subTest(has_role=role):
                self.assertTrue(farmer.has_role(role))

    def test_staff_users_have_the_admin_role(self):
        admin = get_user_model().objects.create_user(
            username="staff-role-user",
            phone_number="+251911111132",
            password=self.pin,
            is_staff=True,
        )

        self.assertTrue(admin.has_role(UserRole.ADMIN))
        self.assertTrue(
            admin.groups.filter(name=role_group_name(UserRole.ADMIN)).exists()
        )

    def test_virtual_users_cannot_use_protected_roles(self):
        user = self.make_user(username="virtual-role-user")
        VirtualAgent.objects.create(
            user=user,
            role=VirtualAgent.Role.FARMER,
            persona_label="Virtual farmer",
        )
        user.refresh_from_db()

        self.assertTrue(user.has_role(UserRole.AI_VIRTUAL_USER))
        self.assertFalse(
            has_any_role(
                user,
                UserRole.ADMIN,
                UserRole.FARMER,
                UserRole.SUPPLIER,
            )
        )

    def test_user_admin_add_form_supports_role_assignment(self):
        admin = get_user_model().objects.create_superuser(
            username="user-admin",
            phone_number="+251911111131",
            password=self.pin,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("admin:users_customuser_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "groups")

    def test_profile_update_renders_account_and_profile_management_controls(self):
        user = self.make_user()
        self.client.force_login(user)

        response = self.client.get(reverse("users:profile_update"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_update.html")
        self.assertContains(response, user.phone_number)
        self.assertContains(response, "Public profile")
        self.assertContains(response, "Contact and social links")
        self.assertContains(response, reverse("users:password_change"))
        self.assertContains(response, 'id="profile-picture-preview"')

    def test_user_can_change_their_pin_without_losing_their_session(self):
        user = self.make_user()
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:password_change"),
            {
                "current_pin": self.pin,
                "new_pin": "7391",
                "confirm_pin": "7391",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:password_change_done"),
            fetch_redirect_response=False,
        )
        self.assertEqual(self.client.get(reverse("users:dashboard")).status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("7391"))
