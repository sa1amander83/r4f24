from django import template

register = template.Library()

@register.filter(name='percent')
def percent(value, arg):
    try:
        if arg==5:
            return round(float(value)*100/900)
        elif arg==4:
            return round(float(value)*100/400)
        elif arg==3:
            return round(float(value)*100/200)
        elif arg==2:
            return round(float(value))
        elif arg==1:
            return round(float(value)*2)
    except (ValueError, ZeroDivisionError):
        return None