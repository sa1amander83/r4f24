from celery import shared_task

from core.models import CustomUser


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def count_widgets():
    return CustomUser.objects.count()


@shared_task
def rename_widget(widget_id, name):
    w = CustomUser.objects.get(id=widget_id)
    w.name = name
    w.save()