from django.urls import path, include

app_name='groups'
from .views import MyGroup, addRunnerToGroup, GroupsListView, add_group

urlpatterns = [
    path('profile/<slug:username>/mygroup/', MyGroup.as_view(), name='mygroup'),
    path('profile/<slug:username>/addgroup/', add_group, name='addgroup'),
    path('profile/<slug:username>/select_group/', GroupsListView.as_view(), name='group_list'),
    path('profile/<slug:username>/add_to_group/<slug:group>/', addRunnerToGroup, name='add_runner_to_group'),
]