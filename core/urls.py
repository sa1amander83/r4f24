from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from core.views import IndexView, CatListView, RunnersCatView

urlpatterns = [

    path('',IndexView.as_view(), name='index'),
    path('cat_selected/<slug:cat>/', CatListView.as_view(), name='cat_selected'),
    # path('runnercat_selected/<slug:cat>/', RunnersCatView.as_view(), name='runnercat_selected'),
    path('runnercat_selected/<slug:cat>&<int:age>/', RunnersCatView.as_view(), name='runnercat_selected'),





]