import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

URL = "https://www.billboard.com/charts/hot-100/"
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

# Spotify Authentication:
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
    )
)
user_id = sp.current_user()["id"]

# Users date input of choice:
date = input("Which year do you want to travel to? (YYYY-MM-DD): ")

# URL request:
response = requests.get(url="https://www.billboard.com/charts/hot-100/" + date)
response.raise_for_status()
print(response.status_code, "\n")

# Scraping data using BeautifulSoup:
soup = BeautifulSoup(response.text, "html.parser")
songs = soup.findAll(
    name="span",
    class_="chart-element__information__song"
)
song_names = [song.getText() for song in songs]

# Saving songs list to an external file:
with open("top_100_songs.txt", mode="w") as txt_file:
    for song in song_names:
        txt_file.write(f"{song}\n")

song_uris = []
year = date.split("-")[0]
print(year)
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")

    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

#Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} best hits",
    public=False
)

#Adding songs found into the new playlist
sp.user_playlist_add_tracks(
    user=user_id,
    playlist_id=playlist["id"],
    tracks=song_uris
)
