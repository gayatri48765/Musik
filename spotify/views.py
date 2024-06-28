from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.views.decorators.csrf import csrf_exempt
import requests,json,base64, urllib.parse,credentials,spotipy
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

# Create your views here.

# Var
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
            # Spotify Login
        
            # Create a SpotifyOAuth object
            sp_oauth = SpotifyOAuth(client_id=credentials.CLIENT_ID, 
                            client_secret=credentials.CLIENT_SECRET, 
                            redirect_uri=REDIRECT_URI, 
                            scope = credentials.scope)
            # Get the authorization URL
            url = sp_oauth.get_authorize_url()
            # Redirect the user to the Spotify login page
            return HttpResponseRedirect(url)
            # return render(request, "home.html", {'fname':fname})
        else:
            messages.error(request, 'Bad Credentials')
            return redirect('home')
    return render(request,'login.html')

def cback(request):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=credentials.CLIENT_ID,
                            client_secret=credentials.CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI, 
                            scope=credentials.scope)

    # Get the authorization code from the query parameters
    code = request.GET.get("code")

    # Request an access token using the authorization code
    token_info = sp_oauth.get_access_token(code=code, check_cache=False)

    # Extract the access token
    access_token = token_info["access_token"]

    # Store the access token in a secure way (e.g. in a session or database)
    request.session["access_token"] = access_token

    # return HttpResponseRedirect("/home/")
    return redirect('home')
    # return render(request, 'home.html',{'access_token': access_token})

def home(request):
    # Retrieve the access token from the session
    access_token = request.session.get('access_token')

    # Pass the access token to the template
    return render(request, 'home.html', {'access_token': access_token})

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
         # Get the access token from the session
        access_token = request.session.get("access_token")
        # print('\n\n ACCESS TOKEN: ', access_token, '\n\n')

        # Create a Spotipy client using the access token
        sp = spotipy.Spotify(auth=access_token)

        # Make a request to the Spotify API to retrieve the user's profile information
        response = sp.me()

        # Check if the request was successful
        if response is not None:
            # The access token is valid
            print("The access token is valid.\n\n")
        else:
            # The access token is invalid or has expired
            print("The access token is invalid or has expired.\n\n")

        # Set the username
        # username = credentials.username

        # Make the HTTP GET request to the Spotify API
        response = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")

        # Extract the top tracks from the response
        top_tracks = response["items"]

         # Create a list of dictionaries representing the top tracks
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

        # print tracks list to console
        print("\n\n\n\nLIST OF TRACKS:",top_tracks[0]['album']['images'][1]['url'])
        print(json.dumps(top_tracks[0], sort_keys=True, indent=4))

        print("TRACK ID")
        print(tracks[0]['track_id'])
        # Return a JSON response containing the top tracks
        # return JsonResponse(track_info, safe=False)
        return render(request, 'top_tracks.html',{'track':tracks})

    else:
        error = "An error has occurred"
        return error
    
def start_playback(request, song_id):
    # Get the access token from the session
    access_token = request.session.get("access_token")

    # Create a Spotipy client using the access token
    sp = spotipy.Spotify(auth=access_token)

    # Start playing the specified track
    sp.start_playback(uris=[f"spotify:track:{song_id}"])

    # Render the template
    return render(request, "spotify_player.html")

    
def home(request):
    return render(request, 'home.html')