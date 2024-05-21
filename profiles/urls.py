from django.urls import path, include


from .views import ProfileUser
urlpatterns = [

    path('<str:username>/', ProfileUser.as_view(),name='profile'),# path(r'accounts/profile/$', ProfileUser.as_view(), name='profile'),

]