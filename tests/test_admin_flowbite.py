from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Book


class AdminFlowbiteTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.username = "admin"
        cls.password = "password123"
        cls.user = get_user_model().objects.create_superuser(
            username=cls.username,
            email="admin@example.com",
            password=cls.password,
        )
        cls.book = Book.objects.create(title="The Flowbite Book", author="Tester")

    def setUp(self) -> None:
        self.client: Client = Client()

    def login(self) -> None:
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in, "Failed to authenticate test client")

    def test_login_page_renders_flowbite_styles(self) -> None:
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "flowbite-admin.css")
        self.assertContains(response, "Sign in to your account")

    def test_admin_index_displays_sidebar_navigation(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "flowbite-admin.css")
        self.assertContains(response, "data-drawer-target=\"logo-sidebar\"")
        self.assertContains(response, "id=\"logo-sidebar\"")

    def test_change_list_uses_flowbite_layout(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:admin_tests_book_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rounded-2xl border border-gray-200")
        self.assertContains(response, "flowbite-admin.css")

    def test_change_form_has_flowbite_form_controls(self) -> None:
        self.login()
        url = reverse("admin:admin_tests_book_change", args=[self.book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rounded-2xl border border-gray-200 bg-white")
        self.assertContains(response, "bg-white p-4 shadow-sm ring-1 ring-gray-100")

    def test_delete_confirmation_template_renders(self) -> None:
        self.login()
        url = reverse("admin:admin_tests_book_delete", args=[self.book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete confirmation")
        self.assertContains(response, "Yes, I’m sure")

    def test_change_form_submission_roundtrip(self) -> None:
        self.login()
        url = reverse("admin:admin_tests_book_change", args=[self.book.pk])
        response = self.client.post(
            url,
            {
                "title": "Updated Flowbite Book",
                "author": "Tester",
                "published": "2024-01-01",
                "_save": "Save",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "was changed successfully")

    def test_change_list_delete_action_confirmation(self) -> None:
        self.login()
        response = self.client.post(
            reverse("admin:admin_tests_book_changelist"),
            {
                "action": "delete_selected",
                "select_across": 0,
                "index": 0,
                "_selected_action": [self.book.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, "Yes, I’m sure")
