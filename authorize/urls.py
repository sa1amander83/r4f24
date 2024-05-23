from django.urls import path

from authorize.views import RegisterUser, LoginUser, logout_user
app_name='authorize'
urlpatterns=[
path('register/', RegisterUser.as_view(), name='register'),
path('login/', LoginUser.as_view(),name='login'),
path('logout/', logout_user,name='logout'),


    ]