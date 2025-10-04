from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from flowbite_admin import FlowbiteAdminSite

from .models import Book


class ProjectAdminSite(FlowbiteAdminSite):
    """Custom admin site used by the test project."""

    site_header = "Flowbite Admin"
    site_title = "Flowbite Admin"
    index_title = "Project administration"

    def get_app_list(self, request, app_label=None):  # type: ignore[override]
        """Return the list of installed apps for the index dashboard."""

        app_list = super().get_app_list(request, app_label)

        if app_label is not None:
            # When Django asks for a single app index, return the list untouched so
            # the framework can render the requested page without hitting our
            # custom ordering logic below.
            return app_list

        return sorted(app_list, key=lambda app: app["name"].casefold())


project_admin_site = ProjectAdminSite(name="project_admin")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published")
    search_fields = ("title", "author")
    list_filter = ("published",)


project_admin_site.register(Book, BookAdmin)

UserModel = get_user_model()
project_admin_site.register(UserModel, UserAdmin)
