from django.db.models.signals import post_delete
from django.dispatch import receiver, Signal
from profiles.models import RunnerDay


del_signal= Signal()
@receiver(post_delete, sender=RunnerDay)
def my_handler(sender, **kwargs):
    pass