from django.urls import path, include

app_name='profile'
from .views import ProfileUser, InputRunnerDayData

urlpatterns = [

    path('<slug:username>/', ProfileUser.as_view(),name='profile'),# path(r'accounts/profile/$', ProfileUser.as_view(), name='profile'),
    path('<slug:username>/addrunday/', InputRunnerDayData.as_view(), name='addrunday'),
]