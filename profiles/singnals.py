from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from profiles.models import RunnerDay
from .tasks import get_best_five_summ,calc_stat, start_save
@receiver(post_save, sender=RunnerDay)
def runner_day_saved(sender, instance, **kwargs):
    # calc_stat.delay(runner_id=instance.runner.id, username=instance.runner)
    get_best_five_summ.delay()

@receiver(post_delete, sender=RunnerDay)
def runner_day_deleted(sender, instance, **kwargs):
    # calc_stat.delay(runner_id=instance.runner.id, username=instance.runner)
    get_best_five_summ.delay()

@receiver(post_save, sender=RunnerDay)
def save_runner_day_data(sender, instance, created, **kwargs):
    if created:
        start_save.delay(instance.pk)