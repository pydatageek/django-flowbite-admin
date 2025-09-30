"""Template tags for Flowbite admin forms."""
from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def render_field(field: Any, /, **attrs: Any) -> str:
    """Render a form field with the provided widget attributes."""
    return field.as_widget(attrs=attrs)
