import sqlite3
conn = sqlite3.connect('files/db.sqlite',check_same_thread=False)
cur = conn.cursor()

import configparser  # импортируем библиотеку
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from pytube import Playlist
import os
import youtube_dl
import re


STATUS_CODE_JUST_DOWNLOADED = 0
path = os.path.abspath("files/")
os.environ["PATH"] += os.pathsep + path
conn = sqlite3.connect('files/db.sqlite',check_same_thread=False)
cur = conn.cursor()

# --- Main Menu ---
#Создаем кнопки
btn_main = KeyboardButton('Главное меню')
btn_music = KeyboardButton('Музыка') # скачивание музыки с youtube
btn_travel = KeyboardButton('Турагентство') # кнопка для вызова парсера для турагенства и публикации в вк
btn_camera = KeyboardButton('Камера') # кнопка для вызова камеры
btn_english = KeyboardButton('Английский') # кнопка для вызова парсера

main_menu = ReplyKeyboardMarkup(resize_keyboard = True) # чтобы кнопки не были во весь экран
main_menu.add(btn_music, btn_travel, btn_camera, btn_english, btn_main)


# --- Full Music menu ---
btn_music_download = KeyboardButton('Скачать')
btn_music_change = KeyboardButton('Редактировать плейлист')
music_menu = ReplyKeyboardMarkup(resize_keyboard = True)
music_menu.add(btn_music_download, btn_music_change)

# --- Shorted Music menu ---
music_smenu = ReplyKeyboardMarkup(resize_keyboard = True)
music_smenu.add(btn_music_change)


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
TOKEN = config["Telegram"]["TOKEN"] # обращаемся как к обычному словарю!
print(TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# @dp.callback_query_handler(text = 'button1')
# async def process_callback_button1(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')

def makedb():
    """Create Database if not exists"""

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS "Users" (
        	"id" INTEGER,
        	"user_name" TEXT,
        	"playlist_url"	TEXT);

        CREATE TABLE IF NOT EXISTS "Playlist" (
            "id" INTEGER,
        	"user_id" INTEGER,
            "url" TEXT,
            "status" INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT));
        '''
    )

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """This handler will be called when user sends `/start`"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    #проверим есть ли пользователь в базе
    cur.execute('SELECT * FROM Users WHERE id = ?',(user_id,))
    row = cur.fetchone()
    conn.commit()
    if row is None:
        cur.execute('INSERT INTO Users (id, user_name) VALUES (?, ?)',(user_id, first_name))#update status 1 when it will be deployed
        conn.commit()
        await bot.send_message(message.from_user.id, "Вы были записаны базу данных")
    else:
        print("Пользователь " + first_name + " вошел")
    await message.reply("Привет!\nНапиши мне что-нибудь!",reply_markup=main_menu)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    """This handler will be called when user sends `/help`"""
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler()
async def echo_message(message: types.Message):
    """This handler will be called when user sends any other command"""
    user_id = message.from_user.id

    if message.text == 'Музыка':
        #проверим есть ли ссылка на плейлист для этого пользователя
        cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
        row = cur.fetchone()
        conn.commit()
        if row is None:
            await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
        else:
            await bot.send_message(message.from_user.id, "Плейлист найден url = " + str(row[0]))
            await message.reply("Выберите действие",reply_markup=music_menu)

    elif message.text == 'Скачать':
        cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
        row = cur.fetchone()
        conn.commit()
        if row is None:
            await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
        else:

            url = str(row[0])
            await bot.send_message(message.from_user.id, "Начинается скачивание плейлиста по url = " + url)
            link = Playlist(url)
            path = 'files/users/' + str(message.from_user.id)
            try:
                os.chdir(path)
            except FileNotFoundError:
                os.mkdir(path)
                os.chdir(path)
            except:
                print("Other error")
            options = {
                'format': 'bestaudio/best',
                'extractaudio' : True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            ydl = youtube_dl.YoutubeDL(options)
            count = 0
            for url in link.video_urls:
                #print("s " + url)

                cur.execute('SELECT id FROM Playlist WHERE url = ?',(url,))
                row = cur.fetchone()
                conn.commit()
                if row is None:
                    count = count + 1
                    result = 'NONE'
                    try:#скачивание самого файла и получение результата
                        with ydl:#GOOGLE
                            result = ydl.extract_info(
                                url,
                                download = True
                            )
                    except:
                        print("[Error] Проблема с соединением при скачивании файла " + url)

                    if result != 'NONE':

                        if 'entries' in result:
                            # Can be a playlist or a list of videos
                            video = result['entries'][0]
                        else:
                            # Just a video
                            video = result
                        video_title = video['title']

                        pattern = '=([\w\-\/]*)'
                        #m = re.search(pattern,url)

                        filename = video_title + '.' + options['postprocessors'][0]['preferredcodec']
                        print("filename " + filename)

                        cur.execute('INSERT INTO Playlist (user_id, url, status) VALUES (?, ?, ?)',(message.from_user.id, url, STATUS_CODE_JUST_DOWNLOADED))#update status 1 when it will be deployed
                        conn.commit()

                        try:
                            audio = open(filename, 'rb')
                        except:
                            print("Не удается открыть файл" + filename)
                        try:
                            await bot.send_audio(message.from_user.id, audio, performer = filename, title = video_title)
                            os.remove(filename)
                        except ConnectionResetError as ECONNRESET:
                            print("Произошел разрыв соединения с пользователем " + str(message.from_user.id))
                        except:
                            print("Файл не был отправлен по причине потери соединения с " + str(message.from_user.id) + "\n Вероятно требуется синхронизация времени с мировым")

            if count == 0:
                await bot.send_message(message.from_user.id, "Новых саундтреков нет")
            else:
                await bot.send_message(message.from_user.id, "Добавлено " + str(count) + " саундтрек(ов)")

    elif message.text == 'Редактировать плейлист':
        await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        if 'https://www.youtube.com/playlist?list' in message.text:
            link = message.text
            cur.execute('UPDATE Users SET playlist_url = ? WHERE id = ?',(link,user_id))
            row = cur.fetchone()
            conn.commit()
            await bot.send_message(message.from_user.id, "Ссылка была успешно добавлена " + link)
        else:
            await bot.send_message(message.from_user.id, message.text)

if __name__ == '__main__':
    makedb()
    executor.start_polling(dp)
