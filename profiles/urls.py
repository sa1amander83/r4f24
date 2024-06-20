from django.urls import path, include

app_name='profile'
from .views import ProfileUser, InputRunnerDayData, EditRunnerDayData, DeleteRunnerDayData,  EditProfile


urlpatterns = [

    path('profile/<slug:username>/', ProfileUser.as_view(),name='profile'),
    path('profile/<slug:username>/addrunday/', InputRunnerDayData.as_view(), name='addrunday'),
    path('profile/<slug:username>/<pk>/editrunday/', EditRunnerDayData.as_view(), name='editrunday'),
    path('profile/<slug:username>/<pk>/delete/', DeleteRunnerDayData.as_view(), name='delete'),
    path('profile/<slug:username>/edit/', EditProfile.as_view(), name='editprofile'),

]