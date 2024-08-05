import os
from celery import Celery
# from celery.schedules import crontab
# from django.contrib.auth import get_user_model
#
# from profiles.tasks import calc_comands

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r4f24.settings')
app = Celery("r4f24", broker='')

app.config_from_object('django.conf:settings', namespace='CELERY')

# загрузка tasks.py в приложение django
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'every': {
#         'task': 'celery.recalc_stat',
#         'schedule': crontab(minute='1'),  # по умолчанию выполняет каждую минуту, очень гибко
#     },  # настраивается
#
# }
#
#
# @app.task
# def recalc_stat():
#     # перерасчет статистики для всех участников
#     users = get_user_model().objects.filter(not_running=False)
#     for user in users:
#         calc_comands(user.username)
#
# app.conf.timezone = 'Europe/Moscow'

#docker pull redis:latest и docker run --name redis-server -p 6379:6379 -d redis:latest
#celery.exe -A r4f24 flower --loglevel=info
#celery -A r4f24 worker --loglevel=info   --pool=solo
