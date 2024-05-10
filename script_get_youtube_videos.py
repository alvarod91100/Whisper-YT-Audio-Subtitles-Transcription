from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import re
from typing import List, Tuple, Dict
import os
from tqdm import tqdm
from utils.misc import normalizeNaming
from dotenv import load_dotenv
load_dotenv()

GOOGLE_YT_KEY = os.getenv('GOOGLE_YT_KEY')
SHORTS_FILTER = False

youtube=build(
    'youtube',
    'v3',
    developerKey=GOOGLE_YT_KEY
)

def getChannelID(channelName:str) -> str: 
    request = youtube.search().list(
        q=channelName,
        type='channel', 
        part = 'id'
    #you can change the channel name here
    )
    response=request.execute()
    channel_id =response['items'][0]['id']['channelId']
    return channel_id

def getChannelUploadsID(channelID:str) -> str:

    request = youtube.channels().list(
        part='contentDetails',
        id=channelID 
    )
    response=request.execute()
    playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return playlist_id

def getPlaylistUploads(playlistID:str, next_page_token= None):
    playlist_items_response=youtube.playlistItems().list(
        #part='contentDetails',
        part='snippet',
        playlistId=playlistID,
        maxResults=50,
        pageToken=next_page_token
        ).execute()
    print(playlist_items_response["items"][0])

def convertDuration(duration_str):
    duration_regex = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    hours, minutes, seconds = duration_regex.match(duration_str).groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    return hours * 3600 + minutes * 60 + seconds

def checkIsShort(videoID:str):
    request = youtube.videos().list(
        part='contentDetails',
        id=videoID 
    )
    response=request.execute()
    duration_str = response["items"][0]["contentDetails"]["duration"]
    duration_s = convertDuration(duration_str)
    is_short = False if duration_s > 60 else True
    return is_short

def getChannelVideos(playlistID, next_page_token = None, filterShortFormContent= True):
    videos = []
    while True:
        playlist_items_response=youtube.playlistItems().list(
                    #part='contentDetails',
                    part='snippet',
                    playlistId=playlistID,
                    maxResults=50,
                    pageToken=next_page_token
        ).execute()

        videos += playlist_items_response['items']
        next_page_token = playlist_items_response.get('nextPageToken')

        if not next_page_token:
            break
    video_urls = []

    for video in tqdm(videos, desc="Parsing videos"):
        try:
            video_id = video['snippet']['resourceId']['videoId']
            if filterShortFormContent:
                if checkIsShort(video_id):
                    continue
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title=video['snippet']['title']
            video_urls.append({'Title':video_title, 'URL':video_url})
        except Exception as e:
            print("Video can't be loaded, maybe it was deleted")
            continue
    return video_urls

def saveToFile(dir:str, filenamePrefix ,video_urls:List):
    file_name = f"{filenamePrefix}_VideoURLS.txt"
    outFile=open(os.path.join(dir, file_name), "w", encoding="utf-8")
    for key in video_urls:
        line=key["URL"] + "  |  " + normalizeNaming(key['Title'])+"\n"
        outFile.write(line)
    return True

if __name__=="__main__":
    scope_choice = int(input("Do you want to download all videos from\n\t1) A specific Channel?\n\t\tor\n\t2) A specific playlist?\nChoice: "))
    if scope_choice == 1:
        CHANNEL_NAME= str(input("Channel Name: "))
        channel_id = getChannelID(CHANNEL_NAME)
        uploads_playlist_id = getChannelUploadsID(channel_id)
        video_urls = getChannelVideos(uploads_playlist_id)
        saveToFile("video_lists", filenamePrefix = CHANNEL_NAME, video_urls=video_urls)
    elif scope_choice == 2:
        uploads_playlist_id = str(input("Paste the playlist ID (you can find it in the URL after the 'list' argument): "))
        video_urls = getChannelVideos(uploads_playlist_id, filterShortFormContent= SHORTS_FILTER)
        prefix = str(input("Introduce Filename Prefix: "))
        saveToFile("video_lists", filenamePrefix = prefix, video_urls=video_urls)

    