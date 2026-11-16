from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminHeaderTests(TestCase):
    def test_superuser_sees_admin_workspace_shortcut(self):
        admin = get_user_model().objects.create_superuser(
            username="header-admin",
            phone_number="+251911111122",
            password="Safe-Test-Password-123!",
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("base:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "admin-workspace-badge")
        self.assertContains(response, reverse("admin_app:dashboard"))
        self.assertContains(response, "Admin dashboard")

    def test_regular_user_does_not_see_admin_workspace_shortcut(self):
        user = get_user_model().objects.create_user(
            username="header-user",
            phone_number="+251911111123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("base:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "admin-workspace-badge")
        self.assertNotContains(response, reverse("admin_app:dashboard"))


class HomeCategorySectionTests(TestCase):
    def test_category_cards_use_descriptive_headings_and_links(self):
        response = self.client.get(reverse("base:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h3 class="category-name">Dairy farm</h3>', html=True)
        self.assertContains(response, '<h3 class="category-name">Poultry</h3>', html=True)
        self.assertContains(response, reverse("dairys:dairy_list"))
        self.assertContains(response, reverse("poultrys:index"))
