from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from core.views import IndexView

urlpatterns = [

    path('',IndexView.as_view(), name='index')




]