"""Template helpers for change list rendering."""
from __future__ import annotations

from typing import Iterable

from django import template

register = template.Library()


@register.filter(name="changelist_rows")
def changelist_rows(results: Iterable, changelist):
    """Return structured row information for the advanced change list."""

    if changelist is None:
        return []
    return changelist.get_result_rows(results)
