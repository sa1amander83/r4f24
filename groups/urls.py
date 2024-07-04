from django.urls import path
from .views import MyGroup, group_list_and_create_view, add_user_to_group
app_name = 'groups'


urlpatterns = [
    path('profile/<slug:username>/mygroup/', MyGroup.as_view(), name='mygroup'),
    path('profile/<slug:username>/myteam/', MyGroup.as_view(), name='myteam'),
    path('profile/<slug:username>/groups/', group_list_and_create_view, name='group_list_and_create'),
    path('add-user-to-group/', add_user_to_group, name='add_user_to_group'),
]
