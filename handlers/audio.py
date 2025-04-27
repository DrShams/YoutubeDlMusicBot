import os
import logging

import re
import traceback
from aiogram import types
from aiogram.types import FSInputFile

from bot import bot
from utils import database
from utils.logging_config import configure_logging


configure_logging()

async def send_to_user_audio(message: types.Message, filename: str, video_url: str):
    """Send audiofile to a user"""
    user_id = message.from_user.id
    pattern = '[^\\.]*'
    m = re.search(pattern,filename)
    track_title = m.group(0)

    filenamepath = os.path.join('files', 'users', str(user_id), filename)

    try:
        filesize = os.stat(filenamepath).st_size / (1024 * 1024)  # megabytes
    except FileNotFoundError:
        current_directory = os.getcwd()  # Get the current working directory
        logging.warning(f"File {filenamepath} not found in {current_directory}")
        await bot.send_message(user_id, f"Файл {filename} не найден в директории: {current_directory}")
        return
    
    if filesize >= 50:
        logging.warning(f"File {filename} was skipped (more than 50 megabytes)")
        await bot.send_message(user_id, f"Файл {filename} был пропущен, т.к. весит больше 50 мегабайт")
        os.remove(filenamepath)
        await update_status_in_db(user_id, video_url, 2)
    else:
        try:
            with open(filenamepath, 'rb') as audio:
                input_file = FSInputFile(filenamepath)
                logging.debug(f"File {filenamepath} successfully opened")
                await bot.send_audio(user_id, input_file, performer=track_title, title=track_title)
                logging.info(f"File {filenamepath} successfully sent to {message.from_user.first_name}")
            os.remove(filenamepath)
            logging.debug(f"File {filenamepath} removed")
            await update_status_in_db(user_id, video_url, 1)
        except ConnectionResetError:
            logging.warning(f"[ConnectionResetError] Connection with the user {message.from_user.first_name} has been interrupted")
        except Exception as err:
            logging.warning(f"[Exception] {traceback.format_exc()}")

#move to utils/database.py in the future
async def update_status_in_db(user_id, video_url, status):
    try:#PUT INTO SEPARATE METHOD
        database.cur.execute(
            'UPDATE Playlist SET status = ? WHERE url = ? AND user_id = ?',
            (status, video_url, user_id)
        )
        database.conn.commit()
        logging.info(f"Status updated to {status} for video_url {video_url}")
    except Exception as e:
        logging.error(f"Failed to update status in database: {e}")