#[1]Standard library imports
import os
import re
import logging

#[2]Related third party imports.
from aiogram import executor, types
from pytube import Playlist

#[3] Local application/library specific imports
from bot import dp, bot
from handlers.audio import send_to_user_audio
from utils import database, youtube_downloader

@dp.message_handler()
async def echo_message(message: types.Message):
    """This handler will be called when user sends any other command"""
    user_id = message.from_user.id
    text = message.text

    if text == 'Музыка':
        await handle_music_command(message, user_id)
    elif text == 'Скачать':
        await handle_download_command(message, user_id)
    elif text == 'Редактировать плейлист':
        await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        await handle_playlist_link(message, user_id, text)


async def handle_music_command(message, user_id):
    database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
    row = database.cur.fetchone()
    if row is None:
        await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        await bot.send_message(user_id, "Плейлист найден url = " + str(row[0]))
        await message.reply("Выберите действие",reply_markup=music_menu)

async def handle_download_command(message, user_id):
    logging.info("user %s clicked 'Download' button", message.from_user.first_name)

    userdirectory = f'files/users/{user_id}'
    if not os.path.isdir(userdirectory):
        os.mkdir(userdirectory)
        logging.info("the folder %s created", userdirectory)
        
    for filename in os.listdir(userdirectory):
        if filename.endswith('.mp3'):
            await bot.send_message(user_id, f"Ожидается отправка {filename} из хранилища...")
            await send_to_user_audio(message, filename, "")

    database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
    row = database.cur.fetchone()
    if row is None:
        await bot.send_message(user_id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        await download_playlist(message, row[0], user_id)#row[0] = playlist_url

async def handle_playlist_link(message, user_id, link):
    if '.com/playlist?list' in link:
        database.cur.execute('UPDATE Users SET playlist_url = ? WHERE id = ?',(link,user_id))
        database.conn.commit()
        await bot.send_message(user_id, f"Ссылка была успешно добавлена {link}")
    else:
        await bot.send_message(user_id, link)

async def download_playlist(message, url, user_id):
    await bot.send_message(user_id, f"Начинается скачивание плейлиста по url = {url}")
    link = Playlist(url)
    count = 0

    userdirectory = os.path.join('files', 'users', str(user_id))

    for video_url in link.video_urls:
        # Check if the URL has already been downloaded
        database.cur.execute('SELECT status FROM Playlist WHERE url = ? AND user_id = ?', (video_url, user_id))
        row = database.cur.fetchone()
        if row and row[0] == 1:
            logging.info(f"File from url {video_url} already downloaded, skipping.")
            continue

        try:
            result = youtube_downloader.downloadfile(video_url, userdirectory)
            logging.info("The file from %s downloaded", video_url)
        except Exception as e:
            logging.warning("Connection issue while downloading file %s: %s", video_url, str(e))
            continue

        if result != 'NONE':
            count += 1

            sanitized_filename = result.get('sanitized_filename')
            if not sanitized_filename:
                continue 

            try:
                STATUS_CODE_JUST_DOWNLOADED = 0
                database.cur.execute(
                    'INSERT INTO Playlist (user_id, url, status) VALUES (?, ?, ?)',
                    (user_id, video_url, STATUS_CODE_JUST_DOWNLOADED)
                )
                database.conn.commit()
            
                await send_to_user_audio(message, sanitized_filename, video_url)
            except Exception as e:
                logging.error(f"Failed to send audio: {e}")

    if count == 0:
        await bot.send_message(user_id, "Новых саундтреков нет")
    else:
        await bot.send_message(user_id, f"Добавлено {count} саундтрек(ов)")
