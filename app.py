"""
Prerequisites

    pip3 install spotipy Flask Flask-Session

    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py

    // on Windows, use `SET` instead of `export`

Run app.py

    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os
from flask import Flask, session, request, redirect, make_response, render_template, jsonify
#from flask import Flask, render_template, flash, redirect, request, session, make_response, jsonify, abort
from flask_session import Session
import spotipy
import funcs


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

#a template i found to initialize the flask app, works pretty well
@app.route('/')
@app.route('/index')
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a> | ' \
        f'<a href="/select_song">Find a Timbre</a>' \


#template
@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

#template
@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()

#template
@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."

#template
@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

#query spotify for available soongs matching the trackname
#since spotipy isn't very well defined for this search, I only allow track name.
@app.route('/select_song', methods =["GET","POST"])
def select_song():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    track_name = "None"
    artist_name = "None"
    if request.method == "POST":
        track_name = request.form.get("tname")
        #artist_name = request.form.get("aname")
        track_info = funcs.search(spotify, f'track:{track_name}')
        
        #package the information i got from spotify and update the page with html.

        #ARTIST - track_info["tracks"]["items"][0]['name']
        #URI - track_info["tracks"]["items"][0]['uri']
        #ALBUM - track_info["tracks"]["items"][0]['album']['name']
        #IMAGE - ["tracks"]["items"][0]['album']['images'][0]['url']
        #Playback - ["tracks"]["items"][0]['external_urls'][0]
        
        send_info = []
        #array of td row info
        #album name[0], track name[1], image[2], playback_url[3], track uri[4], artist name[5] 
        for idx, track in enumerate(track_info["tracks"]["items"]):
            send_info.append([])
            send_info[idx].append(track['name'])
            send_info[idx].append(track['album']['name'])
            send_info[idx].append(track['album']['images'][0]['url'])
            if track['external_urls']:
                send_info[idx].append(track['external_urls']['spotify'])
            else:
                send_info[idx].append("/")
            send_info[idx].append(track['uri'])
            if track['artists'][0]: 
                send_info[idx].append(track['artists'][0]['name'])
            elif track['artists']:
                send_info[idx].append(track['artists']['name'])
            else:
                send_info[idx].append("None")
            
        return make_response(render_template("index.html", sinfo=send_info, selected_name=track_name))
    return make_response(render_template("index.html", selected_name=track_name))


#i am not great at flask, but got this to work then focused on my backend.
#the way i pass data to/from the webpage is definitely bad practice, but i just don't want to fix that part. 
@app.route('/find_timbre', methods =["POST"])
@app.route('/find_timbre', methods =["GET"])
def find_timbre():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if request.method == "POST":
        track_uri = request.form.get("selected")
        return make_response(render_template("find_timbre.html", suri=track_uri))
    else:
        stime  = int(request.args.get('stime', None))
        etime = int(request.args.get('etime', None))
        degree = int(request.args.get('deg', None))
        esize = int(request.args.get('esize', None))
        uri = request.args.get('uid', None)
        #mins = {"deg": [[t_id, min_dist, starts, ends],[]], "deg2": etc}
        data, compare_ct = funcs.get_matches(spotify, uri, stime, etime, degree, esize)
        return make_response(render_template("found_timbre.html", data=data))

@app.route('/found_timbre', methods =["GET", "POST"])
#plotting all windows.
async def found_timbre():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track_uri = ""
    st = ""
    et = ""
    if request.method == "POST":
        track_uri = request.form.get("uri")
        st = request.form.get("start")
        et = request.form.get("end")
        data = funcs.get_matches(spotify, track_uri, st, et)
    return make_response(render_template("found_timbre.html"))

'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT",
            os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))