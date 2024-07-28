from django.db.models.signals import post_delete
from django.dispatch import receiver, Signal
from profiles.models import RunnerDay
from profiles.tasks import calc_start


del_signal= Signal()
@receiver(post_delete, sender=RunnerDay)
def runnerday_post_delete(sender, instance, **kwargs):
    calc_start(instance.user.pk, instance.user.username)