from django.urls import path, include


from .views import ProfileUser, InputRunnerDayData

urlpatterns = [

    path('<str:username>/', ProfileUser.as_view(),name='profile'),# path(r'accounts/profile/$', ProfileUser.as_view(), name='profile'),
    path('<str:usernamer>/addrunday/', InputRunnerDayData.as_view(), name='addrunday'),
]