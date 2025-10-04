"""Custom widgets styled to match the Flowbite admin experience."""
from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.admin import widgets as admin_widgets


class FlowbiteWidgetMixin:
    """Mixin that injects Flowbite-specific classes and data attributes."""

    flowbite_classes: str = ""
    flowbite_data_attributes: dict[str, str] = {}

    def build_attrs(self, base_attrs: dict[str, Any], extra_attrs: dict[str, Any] | None = None) -> dict[str, Any]:
        """Merge Flowbite attributes into the widget configuration."""

        attrs = super().build_attrs(base_attrs, extra_attrs)
        flowbite_class_list = self.flowbite_classes.split()

        if flowbite_class_list:
            existing_classes = attrs.get("class", "").split()
            for class_name in flowbite_class_list:
                if class_name not in existing_classes:
                    existing_classes.append(class_name)
            attrs["class"] = " ".join(existing_classes).strip()

        for attr_name, attr_value in self.flowbite_data_attributes.items():
            attrs.setdefault(attr_name, attr_value)

        return attrs


class FlowbiteTextInput(FlowbiteWidgetMixin, forms.TextInput):
    """Text input styled for Flowbite."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "text"}


class FlowbiteTextarea(FlowbiteWidgetMixin, forms.Textarea):
    """Textarea widget styled for Flowbite."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "textarea"}


class FlowbiteSelect(FlowbiteWidgetMixin, forms.Select):
    """Select widget styled for Flowbite."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "select"}


class FlowbiteSelectMultiple(FlowbiteWidgetMixin, forms.SelectMultiple):
    """Multi-select widget styled for Flowbite."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "select-multiple"}


class FlowbiteCheckboxInput(FlowbiteWidgetMixin, forms.CheckboxInput):
    """Checkbox widget styled for Flowbite."""

    flowbite_classes = (
        "h-4 w-4 rounded border border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 "
        "dark:border-gray-600 dark:bg-gray-700 dark:focus:ring-blue-500"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "checkbox"}


class FlowbiteNumberInput(FlowbiteWidgetMixin, forms.NumberInput):
    """Number input styled for Flowbite."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "number"}


class FlowbiteFilteredSelectMultiple(FlowbiteWidgetMixin, admin_widgets.FilteredSelectMultiple):
    """Flowbite-styled version of Django's filtered multiple select widget."""

    flowbite_classes = (
        "block w-full rounded-lg border border-gray-200 bg-white text-sm text-gray-900 "
        "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-white"
    )
    flowbite_data_attributes = {"data-flowbite-admin-input": "filtered-select-multiple"}


# Ensure the admin uses the Flowbite variant everywhere.
admin_widgets.FilteredSelectMultiple = FlowbiteFilteredSelectMultiple
