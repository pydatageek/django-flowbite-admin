"""Custom ChangeList implementation with advanced filtering support."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from django.contrib.admin.views.main import ALL_VAR, PAGE_VAR, ChangeList

from .forms import AdvancedFilterForm


class AdvancedChangeList(ChangeList):
    """ChangeList that wires the :class:`AdvancedFilterForm` into the admin."""

    advanced_filter_form_class = AdvancedFilterForm

    def __init__(self, *args, **kwargs) -> None:
        self._advanced_filter_form: AdvancedFilterForm | None = None
        self._advanced_lookup_params: Dict[str, List[object]] = {}
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
            return
        self._advanced_lookup_params = form.get_lookup_params()
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
        keys = list(self.get_filters_params().keys())
        return self.get_query_string(remove=keys)

    def get_query_string(self, new_params=None, remove=None):  # type: ignore[override]
        if remove is None:
            remove = []
        else:
            remove = list(remove)
        form = self.get_advanced_filter_form()
        prefix = getattr(form, "param_prefix", "") if form else ""
        if prefix:
            for key in list(remove):
                if not key.startswith(prefix):
                    remove.append(f"{prefix}{key}")
        return super().get_query_string(new_params=new_params, remove=remove)
