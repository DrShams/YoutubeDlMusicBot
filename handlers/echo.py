#[1]Standard library imports
import os
import logging
from utils.logging_config import configure_logging

#[2]Related third party imports.
from aiogram import types, Router
from aiogram.filters import Command
import yt_dlp
import asyncio
message_send_lock = asyncio.Lock()
import configparser

#[3] Local application/library specific imports
from bot import dp, bot
from handlers.audio import send_to_user_audio
from utils import database, youtube_downloader
from utils.buttons import createbuttons



configure_logging()
main_menu = createbuttons()
router = Router()
config = configparser.ConfigParser()
config.read('files/settings.ini')

@router.message()
async def echo_message(message: types.Message):
    """This handler will be called when user sends any other command"""
    user_id = message.from_user.id
    text = message.text

    async with message_send_lock:
        if text == 'Музыка':
            await handle_music_command(message, user_id)
        elif text == 'Скачать':
            await handle_download_command(message, user_id)
        elif text == 'Редактировать плейлист':
            await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
        else:
            await handle_playlist_link(user_id, text)


async def handle_music_command(message, user_id):
    database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
    row = database.cur.fetchone()
    if row is None:
        await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        await bot.send_message(user_id, "Плейлист найден url = " + str(row[0]))
        await message.reply("Выберите действие",reply_markup=main_menu)

async def handle_download_command(message, user_id):
    logging.info("user %s clicked 'Download' button", message.from_user.first_name)

    userdirectory = f'files/users/{user_id}'
    if not os.path.isdir(userdirectory):
        os.mkdir(userdirectory)
        logging.info("the folder %s created", userdirectory)
        
    for filename in os.listdir(userdirectory):
        if filename.endswith('.mp3'):
            logging.info("Ожидается отправка %s из хранилища",  filename)
            await bot.send_message(user_id, f"Ожидается отправка {filename} из хранилища...")
            await send_to_user_audio(message, filename, "")

    database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
    row = database.cur.fetchone()
    if row is None:
        await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        await download_playlist(message, row[0], user_id)

async def handle_playlist_link(user_id, link):
    if '.com/playlist?list' in link:
        database.cur.execute('UPDATE Users SET playlist_url = ? WHERE id = ?',(link,user_id))
        database.conn.commit()
        await bot.send_message(user_id, f"Ссылка была успешно добавлена {link}")
    else:
        await bot.send_message(user_id, link)

async def download_playlist(message, url, user_id):
    try:
        #await bot.send_message(user_id, f"Начинается скачивание плейлиста\nКол-во треков в плейлисте всего {len(link.video_urls)}")
        await bot.send_message(user_id, "Начинается скачивание плейлиста")
        userdirectory = os.path.join('files', 'users', str(user_id))
        count = 0
        video_urls = []

        proxy_user = config.get('Proxy', 'PROXY_USER')
        proxy_pass = config.get('Proxy', 'PROXY_PASS')
        proxy_host = config.get('Proxy', 'PROXY_HOST')
        proxy_port = config.get('Proxy', 'PROXY_PORT')

        proxy_url = f'socks5://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
        
        options = {
            'quiet': True,
            'extract_flat': True,  # Не скачивать, а только получить список
            'skip_download': True,
            'proxy': proxy_url,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                video_urls = [entry['url'] for entry in info['entries']]
            else:
                video_urls = [info['url']]  # если вдруг одна ссылка

        logging.debug(f"Playlist has {len(video_urls)} videos")
        logging.debug(f"Playlist video URLs: {video_urls}")

        for video_url in video_urls:
            # Check if the URL has already been downloaded
            database.cur.execute('SELECT status FROM Playlist WHERE url = ? AND user_id = ? AND status = 0', (video_url, user_id))
            row = database.cur.fetchone()
            if row and (row[0] == 1 or row[0] == 2):
                logging.debug(f"File from url {video_url} already downloaded, skipping.")
                continue

            try:
                result = await youtube_downloader.downloadfile(message, video_url, userdirectory, user_id)
                logging.info(f"The file from {video_url} downloaded ")#\n{result}
            except Exception as e:
                logging.warning("Connection issue while downloading file %s: %s", video_url, str(e))
                continue

            if result != 'NONE':
                count += 1
                #move to utils/database.py in the future
                try:
                    STATUS_CODE_JUST_DOWNLOADED = 0
                    database.cur.execute(
                        'INSERT INTO Playlist (user_id, url, status) VALUES (?, ?, ?)',
                        (user_id, video_url, STATUS_CODE_JUST_DOWNLOADED)
                    )
                    database.conn.commit()
                except Exception as e:
                    logging.error(f"Failed to execute querry: {e}")
                    continue

        if count == 0:
            await bot.send_message(user_id, "Новых саундтреков нет")
        else:
            await bot.send_message(user_id, f"Добавлено {count} саундтрек(ов)")
    except Exception as e:
        logging.error(f"Failed to process the playlist: {e}")
        await bot.send_message(user_id, "Произошла ошибка при обработке плейлиста. Попробуйте еще раз позже.")
