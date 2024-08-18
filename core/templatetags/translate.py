from django import template

register = template.Library()


def get_plural_form(number, forms):
    """Возвращает правильную форму слова в зависимости от числа."""
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]  # "час" или "минута" или "секунда"
    elif 2 <= number % 10 <= 4 and not (11 <= number % 100 <= 14):
        return forms[1]  # "часа" или "минуты" или "секунды"
    else:
        return forms[2]  # "часов" или "минут" или "секунд"


@register.filter(name='format_time')
def format_time(value):
    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = []

    if days > 0:
        result.append(f"{int(days)} {'день' if days == 1 else 'дня' if days < 5 else 'дней'}")

    if hours > 0:
        result.append(f"{int(hours)} {get_plural_form(int(hours), ['час', 'часа', 'часов'])}")

    if minutes > 0:
        result.append(f"{int(minutes)} {get_plural_form(int(minutes), ['минута', 'минуты', 'минут'])}")

    if seconds > 0:
        result.append(f"{int(seconds)} {get_plural_form(int(seconds), ['секунда', 'секунды', 'секунд'])}")

    return ', '.join(result)