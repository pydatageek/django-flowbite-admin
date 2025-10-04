"""Custom ChangeList implementation with advanced filtering support."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set, Tuple

from django.contrib.admin.views.main import ALL_VAR, PAGE_VAR, ChangeList
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import quote
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from .forms.advanced import AdvancedFilterForm


class AdvancedChangeList(ChangeList):
    """ChangeList that wires the :class:`AdvancedFilterForm` into the admin."""

    advanced_filter_form_class = AdvancedFilterForm

    def __init__(self, *args, **kwargs) -> None:
        self._advanced_filter_form: AdvancedFilterForm | None = None
        self._advanced_lookup_params: Dict[str, List[object]] = {}
        self._advanced_query_lookups: Dict[str, str] = {}
        self._advanced_lookup_only: Set[str] = set()
        super().__init__(*args, **kwargs)
        # ``ChangeList.__init__`` calls ``get_queryset`` which initialises the
        # advanced filter form. Expose it for templates after initialisation.
        self.advanced_filter_form = self.get_advanced_filter_form()

    # ------------------------------------------------------------------
    # Form helpers
    # ------------------------------------------------------------------
    def get_advanced_filter_form(self, request=None) -> AdvancedFilterForm | None:
        if self.advanced_filter_form_class is None:
            return None
        if request is None:
            request = getattr(self, "request", None)
        if self._advanced_filter_form is None:
            data = getattr(request, "GET", None) if request is not None else None
            self._advanced_filter_form = self.advanced_filter_form_class(self.model, data=data)
        return self._advanced_filter_form

    def _init_advanced_filters(self, request) -> None:
        form = self.advanced_filter_form_class(self.model, data=request.GET or None)
        self._advanced_filter_form = form
        if not form.is_valid():
            self._advanced_lookup_params = {}
            self._advanced_query_lookups = {}
            self._advanced_lookup_only = set()
            return
        self._advanced_lookup_params = form.get_lookup_params()
        self._advanced_query_lookups = {}
        for field_name, value in form.cleaned_data.items():
            if value in (None, "", []):
                continue
            lookup = getattr(form, "_lookup_map", {}).get(field_name)
            if lookup is None:
                continue
            self._advanced_query_lookups[field_name] = lookup.as_lookup
        request_params = getattr(request, "GET", {})
        if hasattr(request_params, "keys"):
            request_keys = list(request_params.keys())
        else:
            request_keys = list(request_params)
        self._advanced_lookup_only = {
            lookup
            for lookup in self._advanced_lookup_params
            if not any(param.startswith(lookup) for param in request_keys)
        }
        # Synchronise the computed ORM lookups with the parameters Django uses
        # when building query strings so pagination, ordering, and clearing
        # filters continue to work as expected.
        self.filter_params.update(self._advanced_lookup_params)
        for key, values in self._advanced_lookup_params.items():
            if values:
                self.params[key] = values[-1]

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_filters_params(self, params=None):  # type: ignore[override]
        lookup_params = super().get_filters_params(params)
        form = self.get_advanced_filter_form()
        advanced_names = set(form.get_query_parameter_names()) if form else set()
        for key in list(lookup_params.keys()):
            if key in advanced_names:
                del lookup_params[key]
        lookup_params.update(self._advanced_lookup_params)
        return lookup_params

    def get_queryset(self, request, exclude_parameters=None):  # type: ignore[override]
        self.request = request
        if self.advanced_filter_form_class is not None:
            self._init_advanced_filters(request)
        return super().get_queryset(request, exclude_parameters)

    # ------------------------------------------------------------------
    # Template helpers
    # ------------------------------------------------------------------
    def get_result_rows(self, results: Iterable[Any]) -> List[Dict[str, Any]]:
        """Pair the rendered result rows with their objects and actions."""

        object_list = list(self.result_list)
        rendered_rows = list(results)
        rows: List[Dict[str, Any]] = []
        for obj, rendered in zip(object_list, rendered_rows):
            pk_value = getattr(obj, self.pk_attname)
            quoted_pk = quote(pk_value)
            dropdown_id = f"{self.opts.model_name}-row-actions-{quoted_pk}"
            menu_id = f"{dropdown_id}-menu"
            rows.append(
                {
                    "cells": rendered,
                    "form": getattr(rendered, "form", None),
                    "object": obj,
                    "actions": self.get_row_actions(obj),
                    "dropdown_id": dropdown_id,
                    "menu_id": menu_id,
                }
            )
        return rows

    def get_row_actions(self, obj) -> List[Dict[str, Any]]:
        """Return the actions available for ``obj`` in the change list."""

        request = getattr(self, "request", None)
        if request is None:
            return []

        opts = self.opts
        actions: List[Dict[str, Any]] = []

        change_url: str | None = None
        try:
            change_url = self.url_for_result(obj)
        except NoReverseMatch:
            change_url = None
        else:
            change_url = add_preserved_filters(
                {"preserved_filters": self.preserved_filters, "opts": opts},
                change_url,
            )

        view_on_site_url = self.model_admin.get_view_on_site_url(obj)
        can_view = self.model_admin.has_view_permission(request, obj)
        can_change = self.model_admin.has_change_permission(request, obj)

        if can_view:
            external = bool(view_on_site_url)
            view_url = view_on_site_url or change_url
            # Avoid duplicating the edit action when "view" is the same URL.
            if view_url and (external or not can_change):
                action: Dict[str, Any] = {
                    "key": "view",
                    "label": _("View"),
                    "url": view_url,
                }
                if external:
                    action.update({
                        "external": True,
                        "target": "_blank",
                        "rel": "noreferrer noopener",
                    })
                actions.append(action)

        if can_change and change_url:
            actions.append(
                {
                    "key": "edit",
                    "label": _("Edit"),
                    "url": change_url,
                }
            )

        if self.model_admin.has_delete_permission(request, obj):
            try:
                delete_url = reverse(
                    f"admin:{opts.app_label}_{opts.model_name}_delete",
                    args=(quote(getattr(obj, self.pk_attname)),),
                    current_app=self.model_admin.admin_site.name,
                )
            except NoReverseMatch:
                delete_url = None
            else:
                delete_url = add_preserved_filters(
                    {"preserved_filters": self.preserved_filters, "opts": opts},
                    delete_url,
                )
            if delete_url:
                actions.append(
                    {
                        "key": "delete",
                        "label": _("Delete"),
                        "url": delete_url,
                        "danger": True,
                    }
                )

        return actions

    @property
    def advanced_filter_preserved_params(self) -> Iterable[Tuple[str, str]]:
        preserved: List[Tuple[str, str]] = []
        form = self.get_advanced_filter_form()
        param_prefix = getattr(form, "param_prefix", "") if form else ""
        for key, values in self.request.GET.lists():
            if key in {PAGE_VAR, ALL_VAR}:
                continue
            if param_prefix and key.startswith(param_prefix):
                continue
            preserved.extend((key, value) for value in values)
        return preserved

    @property
    def advanced_filter_reset_query(self) -> str:
        form = self.get_advanced_filter_form()
        request = getattr(self, "request", None)
        remove_keys: List[str] = []
        if form is not None and request is not None:
            for name in form.get_query_parameter_names():
                if name in request.GET:
                    remove_keys.append(name)
        return self.get_query_string(remove=remove_keys)

    def get_query_string(self, new_params=None, remove=None):  # type: ignore[override]
        if remove is None:
            remove = []
        else:
            remove = list(remove)
        form = self.get_advanced_filter_form()
        prefix = getattr(form, "param_prefix", "") if form else ""
        if form is not None and remove:
            for key in list(remove):
                if prefix and key.startswith(prefix):
                    lookup_key = self._advanced_query_lookups.get(key)
                    if lookup_key and lookup_key in self._advanced_lookup_only:
                        remove.append(lookup_key)
        if prefix:
            for key in list(remove):
                if not key.startswith(prefix):
                    remove.append(f"{prefix}{key}")
        if remove:
            seen = set()
            remove = [key for key in remove if not (key in seen or seen.add(key))]
        return super().get_query_string(new_params=new_params, remove=remove)
