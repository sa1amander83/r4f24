"""
WSGI config for r4f24 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
def create_wsgi_application():
    pass


app = create_wsgi_application()


# Import the library, create the middleware and wrap your app with it.
import dramatiq_dashboard

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/drama")
app = dashboard_middleware(app)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r4f24.settings')

application = get_wsgi_application()


