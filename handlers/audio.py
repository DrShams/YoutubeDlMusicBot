import os
import re
import logging
import traceback
from aiogram import types
from bot import bot
from utils import database

async def send_to_user_audio(message: types.Message, filename: str, video_url: str):
    """Send audiofile to a user"""
    user_id = message.from_user.id
    pattern = '[^\.]*'
    m = re.search(pattern,filename)
    track_title = m.group(0)

    filenamepath = os.path.join('files', 'users', str(user_id), filename)

    try:
        filesize = os.stat(filenamepath).st_size / (1024 * 1024)  # megabytes
    except FileNotFoundError:
        logging.warning(f"File {filenamepath} not found")
        await bot.send_message(user_id, f"Файл {filename} не найден")
        return
    
    if filesize >= 50:
        logging.warning(f"File {filename} was skipped (more than 50 megabytes)")
        await bot.send_message(user_id, f"Файл {filename} был пропущен, т.к. весит больше 50 мегабайт")
        os.remove(filenamepath)
        try:#PUT INTO SEPARATE METHOD
            STATUS_CODE_SENT = 1
            database.cur.execute(
                'UPDATE Playlist SET status = ? WHERE url = ? AND user_id = ?',
                (STATUS_CODE_SENT, video_url, user_id)
            )
            database.conn.commit()
        except Exception as e:
            logging.error(f"Failed to update status in database: {e}")
    else:
        try:
            with open(filenamepath, 'rb') as audio:
                logging.debug(f"File {filenamepath} successfully opened")
                await bot.send_audio(user_id, audio, performer=track_title, title=track_title)
                logging.info(f"File {filenamepath} successfully sent to {message.from_user.first_name}")
            os.remove(filenamepath)
            logging.debug(f"File {filenamepath} removed")

            try:#DOUBLE CODE DELETE IT !!!
                STATUS_CODE_SENT = 1
                database.cur.execute(
                    'UPDATE Playlist SET status = ? WHERE url = ? AND user_id = ?',
                    (STATUS_CODE_SENT, video_url, user_id)
                )
                database.conn.commit()
            except Exception as e:
                logging.error(f"Failed to update status in database: {e}")
        except ConnectionResetError:
            logging.warning(f"[ConnectionResetError] Connection with the user {message.from_user.first_name} has been interrupted")
        except Exception as err:
            logging.warning(f"[Exception] {traceback.format_exc()}")