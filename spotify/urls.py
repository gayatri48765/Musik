from django.urls import path
from . import  views

urlpatterns = [
    path('',views.base, name="base"),
    path('signin/',views.signin, name="login"),
    path('register/',views.register, name="register"),
    path('cback/',views.cback),
    path('user_toptracks/', views.get_top_tracks, name='get_top_tracks'),
    path('home/',views.home, name='home'),
    path('signout/',views.signout),
    


]

