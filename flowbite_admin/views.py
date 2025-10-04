"""Views for Flowbite admin customizations."""
from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


class UserSettingsView(TemplateView):
    """Display lightweight user settings page within the admin."""

    template_name = "admin/user_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("title", _("Account settings"))
        context.setdefault(
            "settings_description",
            _(
                "Adjust admin preferences, shortcuts, and personal details to tailor the dashboard to your workflow."
            ),
        )
        return context
