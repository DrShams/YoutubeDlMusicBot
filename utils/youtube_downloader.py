import warnings
warnings.filterwarnings("ignore", message="Failed to import \"curl_cffi\" request handler")

import yt_dlp as youtube_dl
import os

import re

def sanitize_filename(filename):
    # Remove non-alphanumeric characters and preserve .mp3 extension
    filename = re.sub(r'[^a-zA-Z0-9]', '', filename)
    return filename + '.mp3'

def downloadfile(url, download_path):
    """Function download files from Youtube and returns dictionary?"""
    options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Save to the specified directory
        'extractaudio' : True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
        #'max_filesize': 5000000#telegram will not allow to sent more than 50 megabytes files
    }
    ydl = youtube_dl.YoutubeDL(options)
    result = 'NONE'
    try:
        with ydl:#download
            result = ydl.extract_info(
                url,
                download = True
            )
            if result:
                filename = result.get('title', 'unknown_title')
                sanitized_filename = sanitize_filename(filename)
                # Rename the downloaded file to the sanitized filename
                original_filepath = os.path.join(download_path, f"{filename}.mp3")
                sanitized_filepath = os.path.join(download_path, sanitized_filename)
                if os.path.exists(original_filepath):
                    os.rename(original_filepath, sanitized_filepath)
                    result['sanitized_filename'] = sanitized_filename
    except Exception as e:
        print(f"[Ошибочка] при скачивании {url} {str(e)}")
    return result