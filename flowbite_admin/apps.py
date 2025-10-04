from types import MethodType

from django.apps import AppConfig
from django.contrib import admin

from .sites import FlowbiteAdminSite, get_user_settings_urlpatterns


class FlowbiteAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flowbite_admin'

    def ready(self) -> None:
        """Ensure the default admin site exposes Flowbite user tools."""

        site = admin.site

        if isinstance(site, FlowbiteAdminSite):
            return

        if getattr(site, "_flowbite_user_settings_registered", False):
            return

        original_get_urls = site.get_urls

        def get_urls(this_site):
            urls = original_get_urls()
            return get_user_settings_urlpatterns(this_site) + urls

        site.get_urls = MethodType(get_urls, site)
        setattr(site, "_flowbite_user_settings_registered", True)
