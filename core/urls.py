from django.urls import path

from core.views import IndexView, CatListView, RunnersCatView, Championate,  \
    StatisticView, RunnersView, RunnersCatGenderView, RunnersCatAgeView, runner_day_results_view, group_statistics_view
from groups.views import view_group

urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('cat_selected/<slug:cat>/', CatListView.as_view(), name='cat_selected'),
    path('runner_category/<int:cat>/', RunnersCatView.as_view(), name='runner_category'),
    path('runner_category/<int:cat>/<int:age>/', RunnersCatAgeView.as_view(), name='runner_category_age'),
    path('runner_category/woman/<int:age>', RunnersCatGenderView.as_view(), name='runner_category_age_female'),
    path('championat/', Championate.as_view(), name='championat'),
    path('comands/<int:group>/', view_group, name='oneTeamView'),
    path('comands/', group_statistics_view, name='allComandsView'),
    path('groups/', group_statistics_view, name='allGroupsView'),
    path('groups/<int:group>/', view_group, name='viewGroup'),
    path('statistic/', StatisticView.as_view(), name='statistic'),
    path('runners/', RunnersView.as_view(), name='runners'),
    path('runners/<slug:cat>/', RunnersView.as_view(), name='runners'),
    path('runner-day-results/<int:day>/', runner_day_results_view, name='runner_day_results'),

]
