from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from poultrys.models import Item


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
        self.assertContains(response, 'class="category-card category-poultry" open')
        self.assertContains(response, '<h3 class="category-name">Poultry</h3>', html=True)
        self.assertContains(response, "Poultry items for sale")
        self.assertContains(response, reverse("poultrys:item_list"))

    def test_category_dropdown_counts_available_listings_and_services(self):
        user = get_user_model().objects.create_user(
            username="category-seller",
            phone_number="+251911111124",
        )
        
        Item.objects.create(
            created_by=user,
            name="Chicken feed",
            slug="chicken-feed",
            description="Poultry feed",
            price="100.00",
        )

        response = self.client.get(reverse("base:index"))

        self.assertEqual(response.context["poultry_item_count"], 1)
        self.assertEqual(response.context["poultry_count"], 1)
        self.assertContains(response, reverse("poultrys:egg_sellers"))
        self.assertContains(response, reverse("poultrys:chicken_sellers_list"))
        self.assertContains(response, reverse("poultrys:veterinary_consultancy"))


class SearchResultsTests(TestCase):
    def test_search_results_link_to_matching_poultry_items(self):
        user = get_user_model().objects.create_user(
            username="search-seller",
            phone_number="+251911111125",
        )
        item = Item.objects.create(
            created_by=user,
            name="Chicken feed",
            description="Nutritious poultry feed",
            price="100.00",
        )

        response = self.client.get(reverse("base:search_results"), {"q": "Chicken"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.name)
        self.assertContains(response, reverse("poultrys:item_detail", args=[item.pk]))
