import re
import requests
import json
from pytube import YouTube, Playlist
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import socket
import random


pl_link_is_valid=False
def getOauthToken(email,password):
    chrome_options = Options() 
    chrome_options.headless=True
    chrome_options.add_argument("--window-size=1920,1080")
    PATH="C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
    driver.get("https://developer.spotify.com/console/post-playlists/")
    link=driver.find_element_by_class_name("input-group-btn")
    link.click()
    time.sleep(2)
    link2=driver.find_element_by_class_name("control-indicator")
    time.sleep(2)
    link2.click()
    time.sleep(2)
    link3=driver.find_element_by_xpath("//*[@id='oauthRequestToken']")
    time.sleep(2)
    link3.click()
    time.sleep(2)
    link4= driver.find_element_by_id("login-username")
    time.sleep(2)
    link4.send_keys(email)
    time.sleep(2)
    link5=driver.find_element_by_id("login-password")
    time.sleep(2)
    link5.send_keys(password)
    time.sleep(2)
    link6=driver.find_element_by_id("login-button")
    time.sleep(2)
    link6.click()
    time.sleep(2)
    if driver.find_elements_by_id("oauth-input"):
        link7=driver.find_element_by_id("oauth-input")
        access_token=link7.get_attribute("value")
        with open("access_token.txt", "w") as f:
            f.write(access_token)
    else:
        with open("access_token.txt", "w") as f:
            f.write("Authentication failed")
    driver.close()

def read_token():
    with open("access_token.txt", "r") as f:
        access_token=f.read()        
        return access_token

#Spotify create playlis
def createPlaylist(playlist_name,email,password):    
    if pl_link_is_valid:  
        header= {"Authorization": f"Bearer {read_token()}", "Content-Type": "application/json"}
        data={"name": playlist_name, "description": "This is a new playlist"}
        url="https://api.spotify.com/v1/users/8hon3mc37max0pvvkn7kyjx1o/playlists"
        r=requests.post(url, headers=header, data=json.dumps(data))
        if r.status_code not in range(200, 299):            
            if(read_token()!="Authentication failed"):  
                getOauthToken(email,password)              
                createPlaylist(playlist_name)
        if "id" in r.json().keys():
            return r.json()["id"]

#Spotify search request
def searchSong(song_name,email,password):
    header={"Authorization":f"Bearer {read_token()}"}
    endpoint = "https://api.spotify.com/v1/search"
    data=urlencode({"q":song_name, "type":"track"})
    lookup_url=f"{endpoint}?{data}"
    r = requests.get(lookup_url, headers=header)   
    if r.status_code not in range(200, 299):        
        if(read_token()!="Authentication failed"):
            getOauthToken(email,password)
            searchSong(song_name,email,password)
    if "tracks" in r.json().keys():
        return r.json()["tracks"]["items"][0]["uri"]



#YT Get song names
def getSpotifyUris(playlist_link,email,password):
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
                    uris.append(searchSong(task.result()[0]["Song"],email,password))       
            return uris

def addSongsToPlaylist(playlist_id,playlist_link,email,password):
    header={"Authorization":f"Bearer {read_token()}"}
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    data={"uris": getSpotifyUris(playlist_link,email,password)}
    r = requests.post(endpoint, headers=header, data=json.dumps(data))
    return r;

def main(email,password,playlist_link,playlist_name):  
    getSpotifyUris(playlist_link,email,password)
    addSongsToPlaylist(createPlaylist(playlist_name,email,password),playlist_link,email,password)


# read_token()