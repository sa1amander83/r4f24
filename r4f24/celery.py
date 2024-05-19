import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r4f24.settings')
app = Celery("r4f24",
             broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))

app.config_from_object('django.conf:settings', namespace='CELERY')

# загрузка tasks.py в приложение django
app.autodiscover_tasks()

# celery -A r4f24  flower
#celery -A r4f24  worker  --loglevel=info

#docker pull redis:latest и docker run --name redis-server -p 6379:6379 -d redis:latest
#
