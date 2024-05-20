from django.urls import path, include


from .views import ProfileUser
urlpatterns = [

    path('profile/', ProfileUser.as_view(), name='profile'),
    # path("__reload__/", include("django_browser_reload.urls")),

]