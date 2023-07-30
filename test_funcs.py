import spotipy
from spotipy import SpotifyClientCredentials
import funcs

def main():
	
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    #spotify, seed, st, et, degree, esize
    #strack = '0XcY2bB4lectIINykHYYDa'
    #rex = spotify.recommendations(seed_tracks=[strack], limit = 10)
    #print(rex)
    #get_matches(spotify, seed, st, et, degree, esize)
    ret = funcs.get_matches(spotify, "spotify:track:1SHB1hp6267UK9bJQUxYvO", 66, 67, 2, 1)
    #ret = funcs.get_matches(spotify, "spotify:track:0XcY2bB4lectIINykHYYDa", 39, 40, 2, 1)
    print(ret)
if __name__ == "__main__":
    main()