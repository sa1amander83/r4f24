from django.urls import path, include

app_name='profile'
from .views import ProfileUser, InputRunnerDayData, EditRunnerDayData, DeleteRunnerDayData, AddFamily, EditProfile, \
    add_family, family_list, my_group, addRunnerToGroup

urlpatterns = [

    path('profile/<slug:username>/', ProfileUser.as_view(),name='profile'),# path(r'accounts/profile/$', ProfileUser.as_view(), name='profile'),
    path('profile/<slug:username>/addrunday/', InputRunnerDayData.as_view(), name='addrunday'),
    path('profile/<slug:username>/<pk>/editrunday/', EditRunnerDayData.as_view(), name='editrunday'),
    path('profile/<slug:username>/<pk>/delete/', DeleteRunnerDayData.as_view(), name='delete'),
    # path('profile/<slug:username>/addfamily', AddFamily.as_view(), name='addfamily'),
    path('profile/<slug:username>/mygroup', my_group, name='mygroup'),
    path('profile/<slug:username>/addfamily', add_family, name='addfamily'),
    path('profile/<slug:username>/edit', EditProfile.as_view(), name='editprofile'),
    path('profile/<slug:username>/myfamily', family_list, name='family_list'),
    path('profile/<slug:username>/add_to_group/', addRunnerToGroup, name='add_runner_to_group'),
    # path('profile/group/<int:group_id>/', GroupView, name='group_view'),
#
]