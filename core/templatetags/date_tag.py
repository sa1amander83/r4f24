from django import template

register = template.Library()

DAYS = ((30, '30 сентября'), (1, '1 октября'), (2, '2 октября'), (3, '3 октября'), (4, '04 октября'),
        (5, '05 октября'), (6, '06 октября'), (7, '07 октября'), (8, '08 октября'), (9, '09 октября'),
        (10, '10 октября'), (11, '11 октября'), (12, '12 октября'), (13, '13 октября'), (14, '14 октября'),
        (15, '15 октября'), (16, '16 октября'), (17, '17 октября'), (18, '18 октября'), (19, '19 октября'),
        (20, '20 октября'), (21, '21 октября'), (22, '22 октября'), (23, '23 октября'), (24, '24 октября'),
        (25, '25 октября'), (26, '26 октября'), (27, '27 октября'), (28, '28 октября'), (29, '29 октября'),
        (30, '30 октября'), (31, '31 октября'))


@register.filter(name='convert_date')
def format_time(value):


    for number, text in DAYS:
        if number == value:
            return text

