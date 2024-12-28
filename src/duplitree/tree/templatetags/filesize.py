from django import template


register = template.Library()


@register.filter
def human_readable_size(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return "0 Bytes"

    if value < 1024:
        return f"{value} Bytes"
    elif value < 1024 ** 2:
        return f"{value / 1024:.2f} KB"
    elif value < 1024 ** 3:
        return f"{value / 1024 ** 2:.2f} MB"
    elif value < 1024 ** 4:
        return f"{value / 1024 ** 3:.2f} GB"
    else:
        return f"{value / 1024 ** 4:.2f} TB"
