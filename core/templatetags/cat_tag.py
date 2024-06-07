from django import template

register = template.Library()


@register.filter(name='cat_tag')
def cat_tag(cat):
    out = ''
    if cat == '1' or cat == 1:
        out = 'Новичок'
    elif cat == '2' or cat == 2:
        out = 'Любитель'
    elif cat == '3' or cat == 3:
        out = 'Профи'

    return out
