from django.urls import path

from authorize.views import RegisterUser, LoginUser, logout_user
app_name='authorize'
urlpatterns=[
path('accounts/register/', RegisterUser.as_view(), name='register'),
path('accounts/login/', LoginUser.as_view(),name='login'),
path('accounts/logout/', logout_user,name='logout'),


    ]