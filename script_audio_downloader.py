from __future__ import unicode_literals
import yt_dlp as youtube_dl
from dataclasses import dataclass
from utils.misc import showFiles, normalizeNaming
import os
from tqdm import tqdm

AUDIO_CODEC = "opus"
AUDIO_DIR= "audio/"
URLS_DIR = "video_lists/"
VIDEO_LIMIT= 100

@dataclass
class youtubedl_options:
    format = 'bestaudio/best'
    post_key = 'FFmpegExtractAudio'
    post_codec = AUDIO_CODEC
    post_quality = '192'

if __name__ =="__main__":
    files= showFiles(URLS_DIR, "text")
    fileChoice= int(input("Enter the file number of the URLs you want to download: "))
    url_file = files[fileChoice]
    VIDEO_LIST_PATH= URLS_DIR + url_file

   

    not_downloaded = {}
    with open(VIDEO_LIST_PATH, "r",encoding="utf-8") as f:
        for line in f:
            not_downloaded[line.split("|")[1].strip().replace("\n", "")] = line.split("|")[0].strip().replace("\n", "")
    
    if os.path.isdir(AUDIO_DIR + url_file.split("_")[0]):
        already_downloaded = [file.split(".")[0].replace("\n", "") for file in os.listdir(AUDIO_DIR + url_file.split("_")[0])]
        not_downloaded = {key: value for key, value in not_downloaded.items() if key not in already_downloaded}
        download_list = list(not_downloaded.values())[:VIDEO_LIMIT]
        print(f"Found {len(already_downloaded)} files already downloaded from list:")
        for file in already_downloaded:
            print(f"\t- {file}")
    
    for title, url in list(not_downloaded.items())[:VIDEO_LIMIT]:
        ydl_opts = {
        'format': youtubedl_options.format,
        'postprocessors': [{
            'key': youtubedl_options.post_key,
            'preferredcodec': youtubedl_options.post_codec,
            'preferredquality': youtubedl_options.post_quality,
        }],
        'outtmpl':AUDIO_DIR + url_file.split("_")[0] + "/" + title + '.%(ext)s'
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])