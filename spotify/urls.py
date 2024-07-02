from django.urls import path
from . import  views

urlpatterns = [
    path('',views.base, name="base"),
    path('signin/',views.signin, name="login"),
    path('register/',views.register, name="register"),
    path('cback/',views.cback),
    path('home/',views.home, name='home'),
    path('home/search',views.search, name='search'),

    path('signout/',views.signout),
    path('user_toptracks/', views.get_top_tracks, name='get_top_tracks'),
    path('liked_songs/', views.get_liked_songs, name='get_liked_songs'),
    path('user_playlist/', views.get_playlist_user, name='get_playlist_user'),
    path('user_albums/', views.get_user_albums, name='get_user_albums'),
    path('user_artists/', views.get_user_artists, name='get_user_artists'),
    path('song/<str:track_id>/', views.song_detail, name='song_detail'),



]

