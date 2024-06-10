from django.urls import path

from core.views import IndexView, CatListView, RunnersCatView, ComandsResults, Championat, OneTeamStat, ComandsView, \
    StatisticView, RunnersView

urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('cat_selected/<slug:cat>/', CatListView.as_view(), name='cat_selected'),
    path('runnercat_selected/<int:cat>/<int:age>/<str:gender>/', RunnersCatView.as_view(), name='runnercat_selected'),
    path('total/', ComandsResults.as_view(), name='totalteamstat'),
    path('championat/', Championat.as_view(), name='championat'),
    path('comands/<slug:comanda>/', OneTeamStat.as_view(), name='oneteamstat'),
    path('comands/', ComandsView.as_view(), name='comandsview'),
    path('statistic/', StatisticView.as_view(), name='statistic'),
    path('runners/', RunnersView.as_view(), name='runners'),


]
