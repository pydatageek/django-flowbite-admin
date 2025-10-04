"""Forms used by the Flowbite admin integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _


@dataclass
class AdvancedLookup:
    """Container describing the lookup associated with a form field."""

    field_name: str
    lookup: str

    @property
    def as_lookup(self) -> str:
        """Return the Django ORM lookup string."""

        return f"{self.field_name}__{self.lookup}" if self.lookup != "exact" else self.field_name


class AdvancedFilterForm(forms.Form):
    """Dynamic form that exposes advanced filtering options for the changelist."""

    param_prefix = "af__"

    def __init__(self, model: type[models.Model], data=None, **kwargs) -> None:
        self.model = model
        super().__init__(data=data, **kwargs)
        self._lookup_map: Dict[str, AdvancedLookup] = {}
        for field in self._iter_filterable_fields():
            for lookup in self._get_lookups_for_field(field):
                form_field = self._build_form_field(field, lookup)
                if form_field is None:
                    continue
                name = self._build_field_name(field.name, lookup)
                self.fields[name] = form_field
                self._lookup_map[name] = AdvancedLookup(field.name, lookup)

    # ------------------------------------------------------------------
    # Field helpers
    # ------------------------------------------------------------------
    def _iter_filterable_fields(self) -> Iterable[models.Field]:
        for field in self.model._meta.get_fields():
            if getattr(field, "many_to_many", False) or getattr(field, "one_to_many", False):
                continue
            if not getattr(field, "concrete", False):
                continue
            yield field

    def _build_field_name(self, field_name: str, lookup: str) -> str:
        return f"{self.param_prefix}{field_name}__{lookup}"

    def _get_lookups_for_field(self, field: models.Field) -> Tuple[str, ...]:
        if isinstance(field, (
            models.CharField,
            models.TextField,
            models.EmailField,
            models.SlugField,
            models.UUIDField,
            models.GenericIPAddressField,
        )):
            return ("contains", "icontains", "exact")
        if isinstance(field, (
            models.IntegerField,
            models.AutoField,
            models.BigIntegerField,
            models.SmallIntegerField,
            models.PositiveIntegerField,
            models.PositiveSmallIntegerField,
            models.FloatField,
            models.DecimalField,
            models.DurationField,
        )):
            return ("exact", "gt", "gte", "lt", "lte")
        if isinstance(field, (models.DateField, models.DateTimeField, models.TimeField)):
            return ("exact", "gt", "lt")
        if isinstance(field, models.BooleanField):
            return ("exact",)
        if isinstance(field, models.ForeignKey):
            return ("exact",)
        return ("exact",)

    def _build_form_field(self, field: models.Field, lookup: str) -> forms.Field | None:
        form_field = field.formfield(required=False)
        if form_field is None:
            return None
        form_field.label = f"{field.verbose_name.title()} ({lookup})"
        # Boolean fields render better as select widgets for tri-state filtering.
        if isinstance(field, models.BooleanField):
            form_field = forms.TypedChoiceField(
                label=form_field.label,
                required=False,
                coerce=lambda value: {
                    "": None,
                    "1": True,
                    "0": False,
                    True: True,
                    False: False,
                    None: None,
                }.get(value, value),
                choices=(
                    ("", "---------"),
                    ("1", _("Yes")),
                    ("0", _("No")),
                ),
            )
        # Lookup values that perform containment searches must always operate on strings.
        if lookup in {"contains", "icontains"}:
            form_field = forms.CharField(label=form_field.label, required=False)
        form_field.widget.attrs.setdefault(
            "class",
            "block w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-gray-900 "
            "focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white",
        )
        return form_field

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_lookup_filters(self) -> Dict[str, object]:
        if not self.is_bound or not self.is_valid():
            return {}
        filters: Dict[str, object] = {}
        for field_name, value in self.cleaned_data.items():
            if value in (None, "", []):
                continue
            lookup = self._lookup_map.get(field_name)
            if lookup is None:
                continue
            filters[lookup.as_lookup] = value
        return filters

    def get_lookup_params(self) -> Dict[str, List[object]]:
        return {
            key: [value]
            for key, value in self.get_lookup_filters().items()
        }

    def get_query_parameter_names(self) -> List[str]:
        return list(self._lookup_map)
