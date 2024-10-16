from django.urls import path

from core.views import IndexView, CatListView, RunnersCatView, Championate, faq, MarathonView, \
    StatisticView, RunnersView, RunnersCatGenderView, RunnersCatAgeView, runner_day_results_view, group_statistics_view, \
    exportcsv
from groups.views import view_group
from core.tasks import recalc_all_groups_and_teams, recalc_func
urlpatterns = [

    path('', IndexView.as_view(), name='index'),
    path('cat_selected/<slug:cat>/', CatListView.as_view(), name='cat_selected'),
    path('runner_category/<int:cat>/', RunnersCatView.as_view(), name='runner_category'),
    path('runner_category/<int:cat>/<int:age>/', RunnersCatAgeView.as_view(), name='runner_category_age'),
    path('runner_category/<int:cat>/<int:age>/<str:gender>/', RunnersCatAgeView.as_view(), name='runner_category_age_gender'),
    path('runner_category/woman/<int:age>', RunnersCatGenderView.as_view(), name='runner_category_age_female'),
    path('championat/', Championate.as_view(), name='championat'),
    path('comands/<int:group>/', view_group, name='oneTeamView'),
    path('comands/', group_statistics_view, name='allComandsView'),
    path('groups/', group_statistics_view, name='allGroupsView'),
    path('groups/<int:group>/', view_group, name='viewGroup'),
    path('faq/', faq, name='faq'),
    path('statistic/', StatisticView.as_view(), name='statistic'),
    path('marathon/', MarathonView.as_view(), name='marathon'),
    path('runners/', RunnersView.as_view(), name='runners'),
    path('runners/<slug:cat>/', RunnersView.as_view(), name='runners'),
    path('runner-day-results/<int:day>/', runner_day_results_view, name='runner_day_results'),
    path('recalc-groups-and-teams/', recalc_all_groups_and_teams, name='recalc_all_groups_and_teams'),
    path('recalc_func/', recalc_func, name='recalc_func'),

    path('exportcsv/', exportcsv, name='exportcsv'),
]
