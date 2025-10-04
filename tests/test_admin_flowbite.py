from __future__ import annotations

import os
from datetime import date
from html.parser import HTMLParser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from .models import Book


call_command("migrate", verbosity=0, run_syncdb=True)


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
        cls.group = Group.objects.create(name="Flowbite Group")
        cls.book = Book.objects.create(title="The Flowbite Book", author="Tester")

    def setUp(self) -> None:
        self.client: Client = Client()

    def login(self) -> None:
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in, "Failed to authenticate test client")

    def assert_content_has_sidebar_offset(self, response) -> None:
        class _ContentParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.content_class: str | None = None

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if self.content_class is not None or tag != "div":
                    return
                attr_map = dict(attrs)
                if attr_map.get("id") == "content":
                    self.content_class = attr_map.get("class", "")

        parser = _ContentParser()
        parser.feed(response.content.decode())
        self.assertIsNotNone(parser.content_class, "Admin template is missing the #content container")
        self.assertIn("sm:ml-64", parser.content_class or "", "#content should include the sidebar offset class")

    def get_reset_href(self, response) -> str:
        class _ResetLinkParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.href: str | None = None
                self._current_href: str | None = None
                self._in_anchor = False

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag != "a":
                    return
                self._in_anchor = True
                self._current_href = dict(attrs).get("href")

            def handle_endtag(self, tag: str) -> None:
                if tag != "a":
                    return
                self._in_anchor = False
                self._current_href = None

            def handle_data(self, data: str) -> None:
                if self._in_anchor and data.strip() == "Reset":
                    self.href = self._current_href

        parser = _ResetLinkParser()
        parser.feed(response.content.decode())
        self.assertIsNotNone(parser.href, "Reset link was not found in the changelist response")
        return parser.href or ""

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

    def test_change_list_displays_advanced_filter_form(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:admin_tests_book_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-accordion=\"collapse\"")
        self.assertContains(response, "name=\"af__title__contains\"")
        self.assertContains(response, 'id="advanced-filter-form"')
        self.assertContains(response, 'form="advanced-filter-form"')

        class _AdvancedFormParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.method: str | None = None

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag != "form":
                    return
                attr_map = dict(attrs)
                if attr_map.get("id") == "advanced-filter-form":
                    self.method = (attr_map.get("method") or "").lower()

        parser = _AdvancedFormParser()
        parser.feed(response.content.decode())
        self.assertEqual(parser.method, "get")

    def test_advanced_filters_limit_queryset(self) -> None:
        extra = Book.objects.create(title="Flowbuddy", author="Helper", published=date(2024, 1, 1))
        other = Book.objects.create(title="Library Almanac", author="Archivist", published=date(2020, 5, 1))

        self.login()
        response = self.client.get(
            reverse("admin:admin_tests_book_changelist"),
            {"af__title__contains": "Flowbuddy", "af__published__gt": "2021-01-01"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, extra.title)
        self.assertNotContains(response, other.title)
        self.assertContains(response, 'value="Flowbuddy"')
        self.assertContains(response, 'value="2021-01-01"')

    def test_advanced_filter_reset_preserves_sidebar_filters(self) -> None:
        published_on = date(2024, 2, 1)
        matching = Book.objects.create(title="Flowbuddy", author="Helper", published=published_on)
        sibling = Book.objects.create(title="Flow State", author="Helper", published=published_on)
        different_date = Book.objects.create(title="Library Almanac", author="Archivist", published=date(2023, 5, 1))

        self.login()
        changelist_url = reverse("admin:admin_tests_book_changelist")
        response = self.client.get(
            changelist_url,
            {
                "published__exact": published_on.isoformat(),
                "af__title__contains": "Flowbuddy",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, matching.title)
        self.assertNotContains(response, sibling.title)

        reset_query = self.get_reset_href(response)

        reset_response = self.client.get(f"{changelist_url}{reset_query}")
        self.assertEqual(reset_response.status_code, 200)
        self.assertContains(reset_response, matching.title)
        self.assertContains(reset_response, sibling.title)
        self.assertNotContains(reset_response, different_date.title)
        self.assertNotContains(reset_response, 'value="Flowbuddy"')
        self.assertEqual(
            reset_response.wsgi_request.GET.get("published__exact"),
            published_on.isoformat(),
        )

    def test_advanced_filter_reset_preserves_shared_sidebar_lookup(self) -> None:
        published_on = date(2024, 2, 1)
        matching = Book.objects.create(title="Flowbuddy", author="Helper", published=published_on)
        sibling = Book.objects.create(title="Flow State", author="Helper", published=published_on)
        different_date = Book.objects.create(title="Library Almanac", author="Archivist", published=date(2023, 5, 1))

        self.login()
        changelist_url = reverse("admin:admin_tests_book_changelist")
        response = self.client.get(
            changelist_url,
            {
                "published__exact": published_on.isoformat(),
                "af__published__exact": published_on.isoformat(),
                "af__title__contains": "Flowbuddy",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, matching.title)
        self.assertNotContains(response, sibling.title)

        reset_query = self.get_reset_href(response)
        reset_response = self.client.get(f"{changelist_url}{reset_query}")
        self.assertEqual(reset_response.status_code, 200)
        self.assertContains(reset_response, matching.title)
        self.assertContains(reset_response, sibling.title)
        self.assertNotContains(reset_response, different_date.title)
        self.assertIsNone(reset_response.wsgi_request.GET.get("af__published__exact"))
        self.assertIsNone(reset_response.wsgi_request.GET.get("af__title__contains"))
        self.assertEqual(
            reset_response.wsgi_request.GET.get("published__exact"),
            published_on.isoformat(),
        )

    def test_advanced_filter_form_is_not_nested_inside_changelist_form(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:admin_tests_book_changelist"))
        self.assertEqual(response.status_code, 200)

        class _FormHierarchyParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self._form_stack: list[str | None] = []
                self.advanced_parent: str | None = None

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag != "form":
                    return
                form_id = dict(attrs).get("id")
                if form_id == "advanced-filter-form":
                    self.advanced_parent = self._form_stack[-1] if self._form_stack else None
                self._form_stack.append(form_id)

            def handle_endtag(self, tag: str) -> None:
                if tag != "form" or not self._form_stack:
                    return
                self._form_stack.pop()

        parser = _FormHierarchyParser()
        parser.feed(response.content.decode())
        self.assertIsNone(parser.advanced_parent, "Advanced filter form should not be nested inside another form")

    def test_bulk_action_submission_succeeds(self) -> None:
        self.login()
        changelist_url = reverse("admin:admin_tests_book_changelist")

        # Initiate the delete_selected action and confirm the intermediate page renders.
        response = self.client.post(
            changelist_url,
            {
                "action": "delete_selected",
                "select_across": "0",
                "index": "0",
                "_selected_action": [str(self.book.pk)],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete the selected")

        # Confirm the deletion through the action and ensure the object is removed.
        confirm_response = self.client.post(
            changelist_url,
            {
                "action": "delete_selected",
                "select_across": "0",
                "index": "0",
                "_selected_action": [str(self.book.pk)],
                "post": "yes",
            },
            follow=True,
        )
        self.assertEqual(confirm_response.status_code, 200)
        self.assertContains(confirm_response, "Successfully deleted")
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_change_form_has_flowbite_form_controls(self) -> None:
        self.login()
        url = reverse("admin:admin_tests_book_change", args=[self.book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rounded-2xl border border-gray-200 bg-white")
        self.assertContains(response, "bg-white p-4 shadow-sm ring-1 ring-gray-100")

    def test_user_changelist_has_sidebar_offset(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:auth_user_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assert_content_has_sidebar_offset(response)

    def test_user_change_form_has_sidebar_offset_and_password_tool(self) -> None:
        self.login()
        url = reverse("admin:auth_user_change", args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_content_has_sidebar_offset(response)
        password_url = reverse("admin:auth_user_password_change", args=[self.user.pk])
        self.assertContains(response, password_url)

    def test_group_changelist_has_sidebar_offset(self) -> None:
        self.login()
        response = self.client.get(reverse("admin:auth_group_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assert_content_has_sidebar_offset(response)

    def test_group_change_form_has_sidebar_offset(self) -> None:
        self.login()
        url = reverse("admin:auth_group_change", args=[self.group.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_content_has_sidebar_offset(response)

    def test_project_admin_profile_link_targets_current_site(self) -> None:
        self.login()
        response = self.client.get(reverse("project_admin:auth_user_changelist"))
        self.assertEqual(response.status_code, 200)
        profile_url = reverse("project_admin:auth_user_change", args=[self.user.pk])
        self.assertContains(response, f'href="{profile_url}"')

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
