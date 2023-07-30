HOW TO RUN THE CODE..

Install Dependencies:
python 3.9+
pip install networkx
#very important to get async because i use that part.
pip install flask[async]
pip install matplotlib
pip install numpy
pip install seaborn
pip install spotipy
versions? any that work


Locally you can set this up pretty easily, you just need an Spotify API Key to get started.
Allow this redirect URI or change it here and in app.py in the __main__
must add these to your environment variables first,
use export KEY='http://127.0.0.1:8080' on Linux.

set SPOTIPY_CLIENT_ID=<key>
set SPOTIPY_CLIENT_SECRET=<key>
set SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080

Now, run the application to finish:
python app.py


For testing purposes you can use test_funcs to skip the webapp portion. 





