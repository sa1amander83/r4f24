import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r4f24.settings')
app = Celery("r4f24")


app.config_from_object('django.conf:settings', namespace='CELERY')

# загрузка tasks.py в приложение django
app.autodiscover_tasks()




#celery.exe -A r4f24.tasks:app beat

# celery.exe -A r4f24.tasks:app flower --loglevel=info
#celery -A r4f24  worker  --loglevel=info

#docker pull redis:latest и docker run --name redis-server -p 6379:6379 -d redis:latest
#
# celery.exe -A r4f24.tasks:app worker --loglevel=INFO --pool=solo
