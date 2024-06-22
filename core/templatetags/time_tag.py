from django import template

register = template.Library()


@register.filter(name='smooth_filter')
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days * 86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hours".format(int(hrs))
        secs = secs - hrs * 3600

    if secs > 60:
        mins = secs // 60
        if mins>9:
            timetot += " {}:".format(int(mins))
        else:
            timetot += " 0{}:".format(int(mins))
        secs = secs - mins * 60

    if secs > 9:
        timetot += "{}".format(int(secs))
    else:
        timetot += "0{}".format(int(secs))

    return timetot

@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)