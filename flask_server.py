
import os
from flask import Flask, session, request, redirect, make_response, render_template, jsonify
from flask_session import Session
import spotipy
import timbre_selection
import read_data

def create_app():
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
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing user-read-playback-state  playlist-modify-private',
                                                   cache_handler=cache_handler,
                                                   show_dialog=True, open_browser=False)

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
            f'<a href="/selection">Select a Song | </a>' \
            f'<a href="/stats_display">Show Stats</a>'

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

    @app.get('/stats_display')
    def stats_display():
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        dfs = read_data.gather_dfs()
        return render_template('stats.html', datasets=dfs)

    @app.get('/selection')
    def selection_get():
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        return render_template('selection.html')

    @app.post('/selection')
    def selection_post():
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        utrack_name = request.form['selection']
        options = timbre_selection.search(spotify, utrack_name)
        track_uris = []
        for item in options['tracks']['items']:
            track_uris.append(item['uri'].replace('spotify:track:', ''))
            #track_uris.append(item['uri'].replace('spotify:track:',''))
        return render_template('selection.html', track_uris=track_uris)
        
    @app.post('/segmentation')
    def segmentation_post():
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        selected_track = request.get_data()
        return render_template('segmentation.html', selected_track=selected_track)

    return app
'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app = create_app()
    app.run(threaded=True, host='152.10.217.87', port=int(os.environ.get("PORT",
            os.environ.get('SPOTIPY_REDIRECT_URI', 5000).split(":")[-1])))
                                                                              
