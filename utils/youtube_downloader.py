import warnings

from handlers.audio import send_to_user_audio
warnings.filterwarnings("ignore", message="Failed to import \"curl_cffi\" request handler")
import logging
from utils.logging_config import configure_logging
configure_logging()

import yt_dlp as youtube_dl
import os

import re

async def sanitize_filename(filename):
    # Remove non-alphanumeric characters and preserve .mp3 extension
    sanitized = re.sub(r'[^a-zA-Z0-9]', '', filename)
    name = sanitized + '.mp3'
    logging.debug(f"Function sanitize_filename: {name}")
    return name

async def downloadfile(message, video_url, download_path):
    """Function download files from Youtube and returns dictionary?"""
    #'max_filesize': 5000000#telegram will not allow to sent more than 50 megabytes files
    options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Save to the specified directory
        'extractaudio' : True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    ydl = youtube_dl.YoutubeDL(options)
    result = 'NONE'
    try:
        with ydl:#download
            result = ydl.extract_info(
                video_url,
                download = True
            )
            if result:
                filename = result.get('title', 'unknown_title')
                original_filename = f"{filename}.mp3"

                sanitized_filename = await sanitize_filename(filename)

                logging.info(f"Original filename: {original_filename}")
                logging.info(f"Sanitized filename: {sanitized_filename}")

                await rename_if_match_and_send(message, video_url, download_path, sanitized_filename)
                
    except Exception as e:
        print(f"[Ошибочка] при скачивании {video_url} {str(e)}")
    return result

async def rename_if_match_and_send(message, video_url, download_path, sanitized_filename):
    # Check existence of any file that matches the original unsanitized name pattern
    matching_file = None
    for f in os.listdir(download_path):
        realfilename = await sanitize_filename(f[:-4])# remove .mp3 and await the result
        if realfilename == sanitized_filename:
            matching_file = f
            break
    
    if matching_file:
        original_filepath = os.path.join(download_path, matching_file)
        sanitized_filepath = os.path.join(download_path, sanitized_filename)
        
        try:
            os.rename(original_filepath, sanitized_filepath)
            logging.info(f"File renamed to {sanitized_filepath}")
            await send_to_user_audio(message, sanitized_filename, video_url)
            return True
        except OSError as e:
            logging.error(f"Failed to rename file: {e}")
            return False
    else:
        logging.error(f"Original file not found for sanitized filename: {sanitized_filename}")
        return False