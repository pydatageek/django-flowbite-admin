from types import MethodType

from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList

from .changelists import AdvancedChangeList
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

        self._patch_model_admin()
        self._patch_default_admin_site(site)
        setattr(site, "_flowbite_user_settings_registered", True)

    def _patch_model_admin(self) -> None:
        """Ensure all ModelAdmin instances use the advanced ChangeList."""

        if getattr(ModelAdmin, "_flowbite_original_get_changelist", None):
            return

        original_get_changelist = ModelAdmin.get_changelist

        def get_changelist(self, request, **kwargs):
            changelist_class = original_get_changelist(self, request, **kwargs)
            if changelist_class is ChangeList:
                return AdvancedChangeList
            return changelist_class

        ModelAdmin._flowbite_original_get_changelist = original_get_changelist
        ModelAdmin.get_changelist = get_changelist

    def _patch_default_admin_site(self, site: admin.AdminSite) -> None:
        """Hook Flowbite tools into the default admin site."""

        original_get_urls = site.get_urls

        def get_urls(this_site):
            urls = original_get_urls()
            return get_user_settings_urlpatterns(this_site) + urls

        site.get_urls = MethodType(get_urls, site)
