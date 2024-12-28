from __future__ import annotations

from django import template
from django.templatetags.static import static
from django.middleware.csrf import get_token
from django.utils.html import format_html

from django_htmx.jinja import django_htmx_script

register = template.Library()
rev = 1

@register.simple_tag(takes_context=True)
def htmx_head(context):
    request = context['request']
    csrf_token = get_token(request)
    return format_html(
        f"""
        <link href="{static('bootstrap/5.3.3/css/bootstrap.min.css')}" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <script src="{static('bootstrap/5.3.3/js/bootstrap.bundle.min.js')}" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="{static('htmx/2.0.4/js/htmx.min.js')}" defer></script>
        <link rel="stylesheet" href="{static('htmx/htmx.styles.css')}">
        <script src="{static('htmx/htmx.scripts.js')}"></script>
        <script>
            const csrfToken = "{csrf_token}";
        </script>
        """
    )
