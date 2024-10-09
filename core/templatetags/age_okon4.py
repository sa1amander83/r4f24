from django import template

register = template.Library()

@register.filter
def years_or_years(value):

    if not isinstance(value, int) or value < 0:
        return value  # Возвращаем значение без изменений, если оно не корректное

    if value % 10 == 1 and value % 100 != 11:
        return f"{value} год"
    elif 2 <= value % 10 <= 4 and not (12 <= value % 100 <= 14):
        return f"{value} года"
    else:
        return f"{value} лет"