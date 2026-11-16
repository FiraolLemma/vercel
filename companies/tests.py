from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from virtual_users.models import VirtualAgent

from .models import Company


class OrganizationOwnershipTests(TestCase):
    def setUp(self):
        self.owner = self.make_user("farm-owner", "+251911111126", "Farmer")
        self.other_farmer = self.make_user(
            "another-farmer",
            "+251911111127",
            "Farmer",
        )
        self.customer = self.make_user(
            "regular-customer",
            "+251911111128",
            "Customer",
        )
        self.company = Company.objects.create(owner=self.owner, name="Green Valley")

    def make_user(self, username, phone_number, role):
        user = get_user_model().objects.create_user(
            username=username,
            phone_number=phone_number,
            password="Safe-Test-Password-123!",
        )
        user.groups.remove(Group.objects.get(name="Customer"))
        user.groups.add(Group.objects.get(name=role))
        return user

    def test_owner_can_create_company(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("companies:company_create"),
            {"name": "Highland Dairy", "location": "Bishoftu"},
        )

        company = Company.objects.get(name="Highland Dairy")
        self.assertRedirects(
            response,
            reverse("companies:company_detail", kwargs={"pk": company.pk}),
            fetch_redirect_response=False,
        )
        self.assertEqual(company.owner_id, self.owner.pk)

    def test_other_user_cannot_view_or_edit_company(self):
        self.client.force_login(self.other_farmer)

        detail_response = self.client.get(
            reverse("companies:company_detail", kwargs={"pk": self.company.pk})
        )
        update_response = self.client.get(
            reverse("companies:company_update", kwargs={"pk": self.company.pk})
        )

        self.assertEqual(detail_response.status_code, 404)
        self.assertEqual(update_response.status_code, 404)

    def test_customer_cannot_create_company(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("companies:company_create"))

        self.assertEqual(response.status_code, 403)

    def test_virtual_account_is_denied_even_if_staff_flag_is_set(self):
        virtual_user = self.make_user(
            "virtual-farmer",
            "+251911111132",
            "Customer",
        )
        VirtualAgent.objects.create(
            user=virtual_user,
            role=VirtualAgent.Role.FARMER,
            persona_label="Virtual farmer",
        )
        virtual_user.is_staff = True
        virtual_user.save(update_fields=("is_staff",))
        self.client.force_login(virtual_user)

        response = self.client.get(reverse("companies:company_create"))

        self.assertEqual(response.status_code, 403)
