""""
URL configuration for r4f24 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from core.views import IndexView
from profiles.tasks import recalculate_balls
from r4f24.views import  import_teams, export_runner_days, export_statistic
from telega.views import TelegramBotView

urlpatterns = [

    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('', include('authorize.urls')),
    path('', include('profiles.urls')),
    path('', include('groups.urls')),
    path('import_teams', import_teams, name='import_teams'),
    path('export_runner_days', export_runner_days, name='export_runner_days'),
    path('export_statistic', export_statistic, name='export_statistic'),
    path('recalculate_balls', recalculate_balls, name='recalculate_balls'),


    path("__debug__/", include("debug_toolbar.urls")),

]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
