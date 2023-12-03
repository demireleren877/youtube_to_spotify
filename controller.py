import requests
import json
from pytube import Playlist
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import url_for, session,redirect
from urllib.parse import urlencode
import spotipy

caches_folder = './.spotify_caches/'
def session_cache_path():
    return caches_folder + session.get('uuid')
pl_link_is_valid=False

def authObject():
    return spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-library-read playlist-modify-public',
            client_id="12fe8879174845bf94e9de513fe889c7",
            client_secret="15ffde4f252e482488d723204e91a21c",
            redirect_uri='http://127.0.0.1:5000/',
            cache_path=session_cache_path(),show_dialog=True
    )

#Spotify create playlis
def createPlaylist(playlist_name):
    auth_manager = authObject()
    if not auth_manager.get_cached_token():
        return redirect('/')
    header= {"Authorization": f"Bearer {auth_manager.get_cached_token()['access_token']}", "Content-Type": "application/json"}
    data={"name": playlist_name, "description": "This is a new playlist"}
    url="https://api.spotify.com/v1/users/{}/playlists".format(getCurrentUser()) #8hon3mc37max0pvvkn7kyjx1o
    r=requests.post(url, headers=header, data=json.dumps(data))
    if "id" in r.json().keys():
        return r.json()["id"]

#Spotify search request
def searchSong(song_name):
    auth_manager = authObject()
    if not auth_manager.get_cached_token():
        return redirect('/')
    header={"Authorization":f"Bearer {auth_manager.get_cached_token()['access_token']}"}
    endpoint = "https://api.spotify.com/v1/search"
    data=urlencode({"q":song_name, "type":"track"})
    lookup_url=f"{endpoint}?{data}"
    r = requests.get(lookup_url, headers=header)   
    if "tracks" in r.json().keys():
        return r.json()["tracks"]["items"][0]["uri"]

def getCurrentUser():
    auth_manager = authObject()
    if not auth_manager.get_cached_token():
        return redirect('/')
    header={"Authorization":f"Bearer {auth_manager.get_cached_token()['access_token']}"}
    endpoint = "https://api.spotify.com/v1/me"
    r = requests.get(endpoint, headers=header)
    return r.json()["id"]


#YT Get song names
def getSpotifyUris(playlist_link):
    playlist = Playlist(playlist_link)
    if (playlist_link.__contains__("https://www.youtube.com/playlist?list=")):
        video_links = Playlist(playlist_link).video_urls
        if len(video_links) > 0:            
            global pl_link_is_valid
            pl_link_is_valid=True      
            names = []      
            def get_video_title():
                for video in playlist.videos:
                    name = video.title
                    names.append(name)
                return names
                               
            processes = []  
            uris=[]
            with ThreadPoolExecutor(max_workers=10) as executor:
                processes.append(executor.submit(get_video_title))
            for tasks in as_completed(processes):
                if tasks.result() is not None:
                    for task in tasks.result():
                        uris.append(searchSong(task))
            return uris

def addSongsToPlaylist(playlist_id,playlist_link):
    auth_manager = authObject()
    if not auth_manager.get_cached_token():
        return redirect('/')
    header={"Authorization":f"Bearer {auth_manager.get_cached_token()['access_token']}"}
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    data={"uris": getSpotifyUris(playlist_link)}
    r = requests.post(endpoint, headers=header, data=json.dumps(data))
    return r

def main(playlist_link,playlist_name):  
    getSpotifyUris(playlist_link)
    addSongsToPlaylist(createPlaylist(playlist_name),playlist_link)
