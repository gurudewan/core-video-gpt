import yt_dlp
import consts
from helpers.gcs_helper import gcs
from helpers.video_metadata import format_video_metadata
import os
import pprint


from filer import find_tmp_file, find_and_format_file

import urllib.parse as urlparse


def quickly_get_youtube_video_id(url):
    """
    Extracts the YouTube video ID from a URL.
    """
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    video_id = query["v"][0]

    return video_id


def get_youtube_video_id(url):
    """
    Returns None if not specifically from YouTube.
    """
    ydl_opts = {
        "extract_flat": True,  # Extract only video ID
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "id" in info and info.get("extractor") == "youtube":
            # with open("tmp/info-example.txt", "w") as f:
            #    f.write(pprint.pformat(info))
            return info["id"]
        else:
            return None


def download_youtube_video(url):
    id = get_youtube_video_id(url)

    save_path = f"tmp/youtube/{id}/{id}.%(ext)s"
    video_path = find_tmp_file(id, "mp4")

    if True:  # video_path is None:
        print("--- video is new ---")
        ydl_opts = {
            # "format": "mp4",  # Specify the format here
            # "format": "bestvideo[height<=480]+bestaudio/best[height<=480]",  # Specify the format here
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
            "writesubtitles": True,  # Write subtitle file
            "writeautomaticsub": True,  # Write automatic subtitle file (YouTube only)
            "subtitlesformat": "srt",  # Download subtitles in srt format
            #'subtitleslangs': ['en', 'en-us'],  # Languages of subtitles to download
            "subtitleslangs": ["en", "en-us"],  # Languages of subtitles to download
            "writeinfojson": True,  # Write video metadata to a .info.json file
            "outtmpl": save_path,  # Output filename template
            "postprocessors": [
                {
                    "key": "FFmpegSubtitlesConvertor",
                    "format": "srt",  # Convert subtitles to srt format
                }
            ],
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Error downloading video: {e}")

    video_path = find_and_format_file(id, "video", "mp4")
    srt_path = find_and_format_file(id, "subs", "srt")
    info_path = find_and_format_file(id, "info", "json")

    print(f"Video path: {video_path}")
    print(f"SRT path: {srt_path}")
    print(f"Info path: {info_path}")

    files = {"video": video_path, "subs": srt_path, "info": info_path}

    return files


def check_subtitles_available(url):
    ydl_opts = {
        "writesubtitles": True,  # Write subtitle file
        "writeautomaticsub": True,  # Write automatic subtitle file (YouTube only)
        "subtitleslangs": ["en"],  # Languages of subtitles to download
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get("requested_subtitles") is None:
            return False  # Captions are not available
        else:
            return True  # Captions are available
