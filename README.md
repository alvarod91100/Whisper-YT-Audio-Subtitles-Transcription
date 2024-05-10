# Whisper-YT-Audio-Transcription
 
This tool is used to transcribe audio using [WhisperX](https://github.com/m-bain/whisperX) into `.srt` subtitles files in batch or individually. As well, it utilizes Google's Youtube API to get be able to query for video information and download the audio from the video in conjunction with [YT-DLP](https://github.com/yt-dlp/yt-dlp). With these, you can choose to download either all the videos from a channel or from a specific playlist. 
It is recommended to run with a CUDA compatible GPU to speed up the transcription and diarization process. In general, a minimum of 4GB VRAM is recommended, but changing the batch size or model in the `transcribe.py` to higher values/bigger models may require up to 16GB VRAM.

## Installation and Setup

1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Install FFMPEG (follow instructions [here](https://ffmpeg.org/download.html))
4. Get or create a Google API key by following the instructions [here](https://developers.google.com/youtube/registering_an_application). Make sure that the API key has access to the **Youtube Data API v3**.
5. Acceopt user agreements for the following HuggingFace models:
    - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
    - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
    - [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization
    )
6. Get or create a HuggingFace API key by following the instructions [here](https://huggingface.co/docs/api-inference/quicktour#get-your-api-token). project.
7. Create a `.env` file in the root directory of the project and follow the format of the `.env.example` file. Fill in the necessary information.

## Usage
The procedure of going from `youtube channel/playlist -> .srt video transcriptions` consists of three parts:
1) Getting a list of the videos links from a channel or playlist and saving them to a file (for now, it only supports `.txt` files). This will save said file in the `video_lists` directory.
2) Downloading the audio from the videos in the list file using the Google API and YT-DLP. This will save the audio files in the `audio` directory.
3) Transcribing the audio files into `.srt` files using WhisperX. This will save the `.srt` files in the `outputs` directory.

With this in mind, the execution of these three steps is separated into three scripts. The execution of each script must be done in the following order, if you want to replicate the above procedure:
1) `get_youtube_videos.py`
2) `audio_downloader.py`
3) `transcribe.py`

Do note that each file has variable parameters at the top that can be changed to suit your needs in case you want to change directory names, where the Whisper model is saved, the model size, batch size, etc.

> ### **Disclaimer**
>
> This tool is intended for educational purposes and personal use only. It is not designed or intended to support the downloading of copyrighted or protected content.