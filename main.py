from bs4 import BeautifulSoup
from datetime import datetime as dt
from datetime import timedelta
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import os
import pprint
import requests
import spotipy

desired_time = None


def grab_desired_date():
    global desired_time
    try:
        user_input_time = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ")
        user_input_dt = dt.strptime(user_input_time, '%Y-%m-%d')
    except ValueError:
        print("Incorrect format, please try again.")
        grab_desired_date()
    else:
        if user_input_dt < dt.now():
            desired_time = user_input_dt
        else:
            print("Date must be in the past.")
            grab_desired_date()


auth_manager = SpotifyOAuth(client_id=os.environ["SPOTIPY_CLIENT_ID"], client_secret=os.environ["SPOTIPY_CLIENT_SECRET"]
                            , redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"], scope="playlist-modify-private",
                            cache_path="token.txt", show_dialog=True)
sp = spotipy.Spotify(oauth_manager=auth_manager)
me = sp.current_user()["id"]

grab_desired_date()
response = requests.get(f'https://www.billboard.com/charts/hot-100/{desired_time.strftime("%Y-%m-%d")}')
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

tracks = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")

top_100_uri = []
for i in range(len(tracks) - 1):
    song_query = sp.search(q=f"track:{tracks[i].text} year: {(desired_time - timedelta(days=365)).strftime('%Y')}-"
                             f"{desired_time.strftime('%Y')}", type="track")
    try:
        top_100_uri.append(song_query["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{tracks[i].text} doesn't exist in spotify. Skipped.")

playlist_id = sp.user_playlist_create(user=me, name=f"Top 100 songs of {desired_time.strftime('%Y-%m-%d')}",
                                      public=False, description=f"Top 100 songs of {desired_time.strftime('%Y-%m-%d')}")

sp.playlist_add_items(playlist_id=playlist_id["id"], items=top_100_uri)
