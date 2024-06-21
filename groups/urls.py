from django.urls import path, include

app_name = 'groups'
from .views import MyGroup, addRunnerToGroup, GroupsListView, add_group, view_group, add_user_to_group, \
    group_list_and_create_view, add_user_to_group

urlpatterns = [
    path('profile/<slug:username>/mygroup/', MyGroup.as_view(), name='mygroup'),
    path('profile/<slug:username>/addgroup/', add_group, name='addgroup'),
    # path('profile/<slug:username>/select_group/', GroupsListView.as_view(), name='group_list'),
    # path('profile/<slug:username>/addgroup/<slug:group>/', GroupsListView.as_view(), name='group_list'),
    # path('profile/<slug:username>/addgroup/<int:group_id>/', add_user_to_group, name='add_user_to_group'),
    path('group/<slug:group>/', view_group, name='viewGroup'),
    path('profile/<slug:username>/groups/', group_list_and_create_view, name='group_list_and_create'),
    path('add-user-to-group/', add_user_to_group, name='add_user_to_group'),
]
