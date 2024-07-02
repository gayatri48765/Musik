from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.views.decorators.csrf import csrf_exempt
import requests,json,base64, urllib.parse,credentials,spotipy
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from django.urls import reverse
AUTH_URL='https://accounts.spotify.com/authorize'
TOKEN_URL='https://accounts.spotify.com/api/token'
API_BASE_URL='https://api.spotify.com/v1/'
REDIRECT_URI='http://127.0.0.1:8000/cback/'

def base(request):
    return render(request, 'base.html')

def signin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user= authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            fname= user.first_name
            sp_oauth = SpotifyOAuth(client_id=credentials.CLIENT_ID, 
                            client_secret=credentials.CLIENT_SECRET, 
                            redirect_uri=REDIRECT_URI, 
                            scope = credentials.scope)
            url = sp_oauth.get_authorize_url()
            return HttpResponseRedirect(url)
        else:
            messages.error(request, 'Bad Credentials')
            return redirect('home')
    return render(request,'login.html')

def cback(request):
    sp_oauth = SpotifyOAuth(client_id=credentials.CLIENT_ID,
                            client_secret=credentials.CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI, 
                            scope=credentials.scope)
    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code=code, check_cache=False)
    access_token = token_info["access_token"]
    request.session["access_token"] = access_token
    return HttpResponseRedirect("/home/")

def home(request):
    access_token = request.session.get("access_token")
    sp = spotipy.Spotify(auth=access_token)
    response = sp.me()
    if response is not None:
        print("The access token is valid.\n\n")
    else:
        print("The access token is sinvalid or has expired.\n\n")
        # Set the username
        # username = credentials.username
    search=[]
    tracks=[]
    if request.method == 'GET':
        response = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")
        top_tracks = response["items"]
        tracks = []
        for track in top_tracks:
            track_info = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "image":track['album']['images'][1]['url'],
                "track_id": track['id']
            }
            tracks.append(track_info)
        # print("\n\n\n\nLIST OF TRACKS:",top_tracks[0]['album']['images'][1]['url'])
        # print(json.dumps(top_tracks[0], sort_keys=True, indent=4))
        # print("TRACK ID")
        # print(tracks[0]['track_id'])
    return render(request, 'home.html', {'access_token': access_token,'track':tracks, 'search':search})


def search(request):
    access_token = request.session.get("access_token")
    sp = spotipy.Spotify(auth=access_token)
    response = sp.me()
    search = []
    if request.method == 'POST':
        search_query = request.POST.get('query', '')
        print("SEARCH!!!!!!")
        print(search_query)

        if search_query:
            response = sp.search(q=search_query, type='show', limit=1)
            result = response['shows']['items']
            # for srch in result:
            #     track_info = {
            #     "name": srch["name"],
            #     "artist": srch["artists"][0]["name"],
            #     "album": srch["album"]["name"],
            #     "image": srch['album']['images'][1]['url'],
            #     "track_id": srch['id']
            # }
            # search.append(track_info)
    return HttpResponse(result)
    # return render(request, 'home.html', {'search':search})
    


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('/')

def register(request):

    if request.method=='POST':
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        myuser= User.objects.create_user(username,email, pass1)
        myuser.first_name=fname
        myuser.last_name=lname

        myuser.save()

        messages.success(request, ' Account created!!')

        return redirect('/signin/')
    return render(request, 'register.html')

def get_top_tracks(request):
    if request.method == 'GET':
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)
        response = sp.me()
        if response is not None:
            print("The access token is valid.\n\n")
        else:
            print("The access token is invalid or has expired.\n\n")

        # Set the username
        # username = credentials.username
        response = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")
        top_tracks = response["items"]
        tracks = []
        for track in top_tracks:
            track_info = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "image":track['album']['images'][1]['url'],
                "track_id": track['id']
            }
            tracks.append(track_info)
        # print("\n\n\n\nLIST OF TRACKS:",top_tracks[0]['album']['images'][1]['url'])
        # print(json.dumps(top_tracks[0], sort_keys=True, indent=4))
        return render(request, 'top_tracks.html',{'track':tracks})

    else:
        error = "An error has occurred"
        return error

def get_liked_songs(request):
    if request.method == 'GET':
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)
        response = sp.me()
        if response is not None:
            print("The access token is valid.\n\n")
        else:
            print("The access token is invalid or has expired.\n\n")
        liked_songs = []
        offset = 0
        limit = 50
        while True:
            response = sp.current_user_saved_tracks(offset=offset)
            # current_user_playlists
            liked_songs.extend(response['items'])
            if len(response['items']) < limit:
                break
            offset += limit

        # Extract the relevant information from the liked songs
        tracks = []
        for item in liked_songs:
            track = item['track']
            track_info = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "image": track['album']['images'][1]['url'],
                "track_id": track['id']
            }
            tracks.append(track_info)

        # Render the template with the liked songs data
        return render(request, 'liked_songs.html', {'track': tracks})

    else:
        error = "An error has occurred"
        return error
    
def get_playlist_user(request):
    if request.method == 'GET':
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)
        response = sp.me()
        if response is not None:
            print("The access token is valid.\n\n")
        else:
            print("The access token is invalid or has expired.\n\n")

        response = sp.current_user_playlists(limit=11, offset=0)
        playlists = response["items"]
        playlist = []
        for plst in playlists:
            lst_info = {
                "name": plst["name"],
                "owner": plst["owner"],
                "href": plst['id'],
                "image":plst['images'][0]['url'],
                "total_songs": plst["tracks"]["total"]
            }
            playlist.append(lst_info)
        # return HttpResponse(playlists)
        return render(request, 'user_playlist.html', {'playlists': playlist})
    else:
        error = "An error has occurred"
        return error
    
def get_user_albums(request):
    if request.method == 'GET':
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)
        response = sp.me()
        if response is not None:
            print("The access token is valid.\n\n")
        else:
            print("The access token is invalid or has expired.\n\n")

        response = sp.current_user_saved_albums(limit=1, offset=0)
        albums_info = response['items']
        albums = []
        for album in albums_info:
            album_info = {
                "name": album["album"]["name"],
                "artist": album["album"]["artists"][0]["name"],
                "image": album["album"]["images"][1]["url"],
                "url":album["album"]["external_urls"]["spotify"]

            }
            albums.append(album_info)
        # return HttpResponse(albums_info)
        return render(request, 'user_albums.html', {'albums': albums})

    else:
        error = "An error has occurred"
        return error

def get_user_artists(request):
    if request.method == 'GET':
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)
        response = sp.me()
        if response is not None:
            print("The access token is valid.\n\n")
        else:
            print("The access token is invalid or has expired.\n\n")

        response = sp.current_user_top_artists(limit=15, offset=0)
        artist_record = response['items']
        artists = []
        for artist in artist_record:
            artist_info = {
                "name": artist["name"],
                "url": artist["external_urls"]["spotify"],
                "image": artist["images"][2]["url"],
            }
            artists.append(artist_info)
        return render(request, 'user_artists.html', {'artists':artists})

    else:
        error = "An error has occurred"
        return error

def song_detail(request, track_id):
    access_token = request.session.get("access_token")
    sp = spotipy.Spotify(auth=access_token)

    # Fetch the song details using the track_id
    track = sp.track(track_id)

    context = {
        'access_token': access_token,
        'track': track,
    }

    return render(request, 'song_detail.html', context)