from django.urls import path

from authorize.views import RegisterUser, LoginUser, logout_user, show_reset, show_reset_success

app_name = 'authorize'
urlpatterns = [
    path('accounts/register/', RegisterUser.as_view(), name='register'),
    path('accounts/login/', LoginUser.as_view(), name='login'),
    path('accounts/logout/', logout_user, name='logout'),
    path('accounts/reset/', show_reset, name='password_change'),
    path('accounts/reset_success/', show_reset_success, name='password_change_success'),

]
