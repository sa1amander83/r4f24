from django.urls import path

from core.views import IndexView, CatListView, RunnersCatView, ComandsResults, Championat, OneTeamStat, ComandsView, \
    StatisticView, RunnersView, RunnersCatGenderView, RunnersCatAgeView, group_list

urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('cat_selected/<slug:cat>/', CatListView.as_view(), name='cat_selected'),
    path('runner_category/<int:cat>/', RunnersCatView.as_view(), name='runner_category'),
    path('runner_category/<int:cat>/<int:age>/', RunnersCatAgeView.as_view(), name='runner_category_age'),
    path('runner_category/woman/<int:age>', RunnersCatGenderView.as_view(), name='runner_category_age_female'),
    path('total/', ComandsResults.as_view(), name='totalteamstat'),
    path('championat/', Championat.as_view(), name='championat'),
    path('comands/<slug:comanda>/', OneTeamStat.as_view(), name='oneteamstat'),
    path('comands/', ComandsView.as_view(), name='comandsview'),
    path('groups/', group_list, name='groupsview'),
    path('statistic/', StatisticView.as_view(), name='statistic'),
    path('runners/', RunnersView.as_view(), name='runners'),
    path('runners/<slug:cat>/', RunnersView.as_view(), name='runners'),

]
