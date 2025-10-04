"""Custom admin site with enhanced dashboard widgets."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import timedelta
from typing import Iterable, List

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, path, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _

from .views import UserSettingsView


def get_user_settings_urlpatterns(site: admin.AdminSite) -> list:
    """Return URL patterns used to power the user settings screen."""

    return [
        path("settings/", site.admin_view(UserSettingsView.as_view()), name="user-settings"),
    ]


class FlowbiteAdminSite(admin.AdminSite):
    """Admin site that powers the Flowbite dashboard widgets."""

    widget_session_key = "flowbite_admin_widget_layout"

    def get_urls(self):
        """Extend default admin URLs with Flowbite-specific views."""

        urls = super().get_urls()
        return get_user_settings_urlpatterns(self) + urls

    def get_default_widget_layout(self, request: HttpRequest) -> List[str]:
        """Return the default order for dashboard widgets."""

        return [
            "kpi-cards",
            "activity-chart",
            "app-list",
            "top-models",
            "recent-actions",
        ]

    # ------------------------------------------------------------------
    # Widget layout persistence
    # ------------------------------------------------------------------
    def get_widget_layout(self, request: HttpRequest) -> List[str]:
        """Retrieve the stored widget layout for the current session."""

        stored: Iterable[str] | None = request.session.get(self.widget_session_key)
        default_layout = self.get_default_widget_layout(request)

        if stored:
            # Filter out widgets that are no longer available and ensure the
            # defaults are appended so the dashboard always shows every widget.
            layout = [widget for widget in stored if widget in default_layout]
            for widget in default_layout:
                if widget not in layout:
                    layout.append(widget)
        else:
            layout = default_layout.copy()
            request.session[self.widget_session_key] = layout

        request.session.modified = True
        return layout

    def save_widget_layout(self, request: HttpRequest, layout: Iterable[str]) -> List[str]:
        """Persist the widget layout in the session."""

        default_widgets = self.get_default_widget_layout(request)
        cleaned_layout = [widget for widget in layout if widget in default_widgets]

        for widget in default_widgets:
            if widget not in cleaned_layout:
                cleaned_layout.append(widget)

        request.session[self.widget_session_key] = cleaned_layout
        request.session.modified = True
        return cleaned_layout

    # ------------------------------------------------------------------
    # Dashboard data helpers
    # ------------------------------------------------------------------
    def get_kpi_cards(self, request: HttpRequest) -> List[dict]:
        """Return data for KPI cards displayed on the dashboard."""

        UserModel = get_user_model()
        total_users = UserModel.objects.count()
        staff_users = UserModel.objects.filter(is_staff=True).count()

        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        previous_period_start = seven_days_ago - timedelta(days=7)

        active_users = None
        new_users = None

        if hasattr(UserModel, "last_login"):
            active_users = UserModel.objects.filter(last_login__gte=seven_days_ago).count()
        if hasattr(UserModel, "date_joined"):
            new_users = UserModel.objects.filter(date_joined__gte=seven_days_ago).count()

        recent_actions = self.get_log_queryset().filter(action_time__gte=seven_days_ago)
        previous_actions = self.get_log_queryset().filter(
            action_time__lt=seven_days_ago, action_time__gte=previous_period_start
        )

        def percentage_change(current: int, previous: int) -> float | None:
            if previous == 0:
                return None if current == 0 else 100.0
            return ((current - previous) / previous) * 100

        kpis = [
            {
                "id": "total-users",
                "title": _("Total users"),
                "value": total_users,
                "badge": _("All accounts"),
                "change": None,
            },
            {
                "id": "staff-users",
                "title": _("Staff members"),
                "value": staff_users,
                "badge": _("With admin access"),
                "change": None,
            },
        ]

        if active_users is not None:
            previous_active = None
            if hasattr(UserModel, "last_login"):
                previous_active = UserModel.objects.filter(
                    last_login__lt=seven_days_ago, last_login__gte=previous_period_start
                ).count()
            kpis.append(
                {
                    "id": "active-users",
                    "title": _("Active this week"),
                    "value": active_users,
                    "badge": _("Logins in last 7 days"),
                    "change": percentage_change(active_users, previous_active or 0),
                }
            )

        if new_users is not None:
            previous_new = UserModel.objects.filter(
                date_joined__lt=seven_days_ago, date_joined__gte=previous_period_start
            ).count()
            kpis.append(
                {
                    "id": "new-users",
                    "title": _("New accounts"),
                    "value": new_users,
                    "badge": _("Joined in last 7 days"),
                    "change": percentage_change(new_users, previous_new),
                }
            )

        current_actions = recent_actions.count()
        previous_actions_count = previous_actions.count()
        kpis.append(
            {
                "id": "recent-actions",
                "title": _("Admin activity"),
                "value": current_actions,
                "badge": _("Changes in last 7 days"),
                "change": percentage_change(current_actions, previous_actions_count),
            }
        )

        return kpis

    def get_activity_chart(self) -> dict:
        """Prepare chart data showing admin actions per day."""

        now = timezone.localdate()
        start_date = now - timedelta(days=6)
        log_model = self.get_log_entry_model()
        log_qs = self.get_log_queryset().filter(action_time__date__gte=start_date)
        grouped = log_qs.values("action_time__date", "action_flag").annotate(total=Count("id"))

        totals = defaultdict(
            lambda: {log_model.ADDITION: 0, log_model.CHANGE: 0, log_model.DELETION: 0}
        )
        for row in grouped:
            totals[row["action_time__date"]][row["action_flag"]] = row["total"]

        labels: List[str] = []
        additions: List[int] = []
        changes: List[int] = []
        deletions: List[int] = []

        for day_index in range(7):
            current_date = start_date + timedelta(days=day_index)
            labels.append(date_format(current_date, format="N j"))
            summary = totals[current_date]
            additions.append(summary[log_model.ADDITION])
            changes.append(summary[log_model.CHANGE])
            deletions.append(summary[log_model.DELETION])

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": str(_("Additions")),
                    "data": additions,
                    "backgroundColor": "rgba(59, 130, 246, 0.45)",
                    "borderColor": "rgba(37, 99, 235, 0.9)",
                    "fill": True,
                    "tension": 0.35,
                },
                {
                    "label": str(_("Changes")),
                    "data": changes,
                    "backgroundColor": "rgba(16, 185, 129, 0.45)",
                    "borderColor": "rgba(5, 150, 105, 0.9)",
                    "fill": True,
                    "tension": 0.35,
                },
                {
                    "label": str(_("Deletions")),
                    "data": deletions,
                    "backgroundColor": "rgba(248, 113, 113, 0.35)",
                    "borderColor": "rgba(220, 38, 38, 0.75)",
                    "fill": True,
                    "tension": 0.35,
                },
            ],
        }

    def get_top_models(self, request: HttpRequest) -> List[dict]:
        """Return object counts for the most populated registered models."""

        stats: List[dict] = []
        for model, _model_admin in self._registry.items():
            manager = getattr(model, "_default_manager", None)
            if manager is None:
                continue

            try:
                count = manager.all().count()
            except (OperationalError, NotImplementedError):
                continue

            if count == 0:
                continue

            model_meta = model._meta
            try:
                admin_url = reverse(
                    f"{self.name}:{model_meta.app_label}_{model_meta.model_name}_changelist"
                )
            except NoReverseMatch:
                admin_url = None

            stats.append(
                {
                    "app_label": model_meta.app_label,
                    "verbose_name": model_meta.verbose_name_plural.capitalize(),
                    "count": count,
                    "admin_url": admin_url,
                }
            )

        stats.sort(key=lambda item: item["count"], reverse=True)
        return stats[:5]

    def get_recent_actions(self, request: HttpRequest, limit: int = 8) -> List["LogEntry"]:
        """Return recent log entries for the current user."""

        return list(
            self.get_log_queryset()
            .filter(user=request.user)
            .select_related("content_type")
            .order_by("-action_time")[:limit]
        )

    def get_topbar_notifications(self, request: HttpRequest, limit: int = 6) -> List[dict]:
        """Return serialized notifications for the header dropdown."""

        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return []

        notifications: List[dict] = []
        for entry in self.get_recent_actions(request, limit=limit):
            localized = timezone.localtime(entry.action_time)
            notifications.append(
                {
                    "id": entry.pk,
                    "message": entry.get_change_message(),
                    "url": entry.get_admin_url(),
                    "timestamp": date_format(localized, format="SHORT_DATETIME_FORMAT"),
                    "relative": timesince(localized),
                }
            )

        return notifications

    def get_log_queryset(self):
        """Provide a shared queryset for admin log lookups."""

        return self.get_log_entry_model().objects.select_related("content_type", "user")

    def get_log_entry_model(self):
        """Return the Django admin log model without triggering early imports."""

        return apps.get_model("admin", "LogEntry")

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def _get_registered_model_keys(self) -> dict[str, str]:
        """Return a mapping of ``app_label_model`` strings to their app labels."""

        return {
            f"{model._meta.app_label}_{model._meta.model_name}": model._meta.app_label
            for model in self._registry
        }

    def _extract_model_key_from_url_name(self, url_name: str | None) -> str | None:
        """Return the ``app_label_model`` key inferred from an admin URL name."""

        if not url_name:
            return None

        suffixes = [
            "_changelist",
            "_add",
            "_change",
            "_delete",
            "_history",
        ]
        for suffix in suffixes:
            if url_name.endswith(suffix):
                return url_name[: -len(suffix)]
        return None

    def _resolve_active_targets(self, request: HttpRequest) -> tuple[str | None, str | None]:
        """Determine which app and model should be marked as active."""

        resolver_match = getattr(request, "resolver_match", None)
        if not resolver_match:
            return None, None

        namespace = resolver_match.namespace or resolver_match.app_name
        if namespace != self.name:
            return None, None

        active_app_label: str | None = resolver_match.kwargs.get("app_label")
        active_model_key: str | None = None

        model_name = resolver_match.kwargs.get("model_name")
        if active_app_label and model_name:
            active_model_key = f"{active_app_label}_{model_name}"

        registered_keys = self._get_registered_model_keys()

        if not active_model_key:
            inferred_key = self._extract_model_key_from_url_name(resolver_match.url_name)
            if inferred_key and inferred_key in registered_keys:
                active_model_key = inferred_key
                active_app_label = active_app_label or registered_keys[inferred_key]

        return active_app_label, active_model_key

    def get_app_list(self, request: HttpRequest, app_label: str | None = None) -> List[dict]:
        """Annotate the default app list with active state metadata."""

        try:
            app_list = super().get_app_list(request, app_label)  # type: ignore[arg-type]
        except TypeError:
            app_list = super().get_app_list(request)
        active_app_label, active_model_key = self._resolve_active_targets(request)

        for app in app_list:
            app_label = app.get("app_label")
            is_active_app = app_label == active_app_label

            for model in app.get("models", []):
                object_name = model.get("object_name", "")
                model_key = f"{app_label}_{object_name.lower()}" if app_label else None
                is_active_model = model_key == active_model_key
                model["is_active_model"] = is_active_model
                if is_active_model:
                    is_active_app = True

            app["is_active_app"] = is_active_app

        return app_list

    # ------------------------------------------------------------------
    # Index view
    # ------------------------------------------------------------------
    def index(self, request: HttpRequest, extra_context: dict | None = None) -> HttpResponse:
        """Render the dashboard with aggregated statistics."""

        if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                payload = json.loads(request.body.decode("utf-8")) if request.body else {}
            except json.JSONDecodeError:
                payload = {}

            if payload.get("action") == "reset":
                layout = self.get_default_widget_layout(request)
                self.save_widget_layout(request, layout)
                return JsonResponse({"status": "ok", "layout": layout})

            if "widget_order" in payload:
                layout = self.save_widget_layout(request, payload["widget_order"])
                return JsonResponse({"status": "ok", "layout": layout})

            return JsonResponse({"status": "noop"})

        app_list = self.get_app_list(request)
        layout = self.get_widget_layout(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "app_list": app_list,
            "kpi_cards": self.get_kpi_cards(request),
            "chart_config": {"activity": self.get_activity_chart()},
            "top_models": self.get_top_models(request),
            "recent_logs": self.get_recent_actions(request),
            "widget_layout": layout,
            "can_manage_widgets": request.user.is_superuser,
        }

        if extra_context:
            context.update(extra_context)

        request.current_app = self.name
        return TemplateResponse(request, self.index_template or "admin/index.html", context)

    def get_user_profile_url(self, request: HttpRequest) -> str | None:
        """Return the admin change URL for the authenticated user, if available."""

        user = getattr(request, "user", None)

        if not getattr(user, "is_authenticated", False):
            return None

        try:
            return reverse(
                f"{self.name}:{user._meta.app_label}_{user._meta.model_name}_change",
                args=[user.pk],
            )
        except NoReverseMatch:
            return None

    def each_context(self, request: HttpRequest) -> dict:
        """Inject extra context needed by all admin templates."""

        context = super().each_context(request)
        context.setdefault("topbar_notifications", self.get_topbar_notifications(request))
        context.setdefault("user_profile_url", self.get_user_profile_url(request))
        return context
