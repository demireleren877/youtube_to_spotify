import requests
import json
from pytube import YouTube, Playlist
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, url_for, session, request, redirect
from urllib.parse import urlencode
from spotipy.oauth2 import SpotifyOAuth
import time
import socket

# hostname = socket.gethostname()
# ipaddress = socket.gethostbyname(hostname)
# path= str(ipaddress)+".txt"
pl_link_is_valid=False
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="12fe8879174845bf94e9de513fe889c7",
            client_secret="15ffde4f252e482488d723204e91a21c",
            redirect_uri=url_for('redirectPage', _external=True),
            scope="user-library-read playlist-modify-public")

#Spotify create playlis
def createPlaylist(playlist_name):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    header= {"Authorization": f"Bearer {session.get('token_info').get('access_token')}", "Content-Type": "application/json"}
    data={"name": playlist_name, "description": "This is a new playlist"}
    url="https://api.spotify.com/v1/users/8hon3mc37max0pvvkn7kyjx1o/playlists"
    r=requests.post(url, headers=header, data=json.dumps(data))
    print(r.json())
    if "id" in r.json().keys():
        return r.json()["id"]

#Spotify search request
def searchSong(song_name):
    header={"Authorization":f"Bearer {session.get('token_info').get('access_token')}"}
    endpoint = "https://api.spotify.com/v1/search"
    data=urlencode({"q":song_name, "type":"track"})
    lookup_url=f"{endpoint}?{data}"
    r = requests.get(lookup_url, headers=header)   
    if "tracks" in r.json().keys():
        return r.json()["tracks"]["items"][0]["uri"]



#YT Get song names
def getSpotifyUris(playlist_link):
    if (playlist_link.__contains__("https://www.youtube.com/playlist?list=")):
        video_links = Playlist(playlist_link).video_urls
        if len(video_links) > 0:            
            global pl_link_is_valid
            pl_link_is_valid=True            
            def get_video_title(link):
                title = YouTube(link).metadata  
                if title.metadata.__len__() != 0:
                    return title                
            processes = []  
            uris=[]
            with ThreadPoolExecutor(max_workers=10) as executor:
                for url in video_links:
                    processes.append(executor.submit(get_video_title, url))
            for task in as_completed(processes):
                if task.result() is not None:
                    uris.append(searchSong(task.result()[0]["Song"]))       
            return uris

def addSongsToPlaylist(playlist_id,playlist_link):
    header={"Authorization":f"Bearer {session.get('token_info').get('access_token')}"}
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    data={"uris": getSpotifyUris(playlist_link)}
    r = requests.post(endpoint, headers=header, data=json.dumps(data))
    return r;

def main(playlist_link,playlist_name):  
    getSpotifyUris(playlist_link)
    addSongsToPlaylist(createPlaylist(playlist_name),playlist_link)
