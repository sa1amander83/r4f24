from django import template

register = template.Library()


@register.filter(name='okon4')
def word_end(value):
    try:
        if value % 10 == 1:
            return f"{value} участник"
        elif 2 <= value % 10 <= 4:
            return f"{value} участника"
        elif 5 <= value % 10 <= 9:
            return f"{value} участников"
        else:
            return f"{value} участников"
    except (ValueError, ZeroDivisionError):
        return None