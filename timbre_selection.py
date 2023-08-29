import spotipy
from spotipy import SpotifyOAuth
import sys
from os import system
import click

#initialize spotipy
def init_sp(): 

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(open_browser=False))
    #spotify = spotipy.Spotify(client_credentials_manager=SpotifyPKCE(username='1292990717')
    return spotify

#display track select options in terminal
#return the selected track dictionary
def display_options(sp, opts):
    for idx, opt in enumerate(opts):
        display_str = str(idx+1) + '.  '
        display_str += opt['album']['name']
        for artist in opt['artists']:
            display_str += '  |  ' + artist['name']    
        display_str += '  |  ' + opt['name']
        print(display_str)

    selection = int(input("Select the correct Track Number: "))
    return opts[selection]

def terminal_search(sp):
    track_name=input("Enter Track Name: ")
    options = sp.search(track_name, type='track')
    selection = display_options(sp, options['tracks']['items'])
    
    
    print(selection['uri'])
    print(sp.current_playback())
    # additional segmentation possible here..
    # I could add a search feature here for segment selection based on the existing segments.
    # Owl Song 18s-19s Hoot
    seg_start=int(input("Enter Segment Start (s): "))
    seg_end=int(input("Enter Segment End (s): "))
    
    #sp.start_playback(selection['uri'])


#search for matching tracks
def search(sp, track_info):
    result = sp.search(track_info, type='track')
    return result

if __name__ == '__main__':
    sp = init_sp()
    terminal_search(sp)
