#[1]Standard library imports
import os
import re
import configparser
import logging

#[2]Related third party imports.
import youtube_dl
import traceback
from aiogram import Bot, Dispatcher, executor, types
from pytube import Playlist

#[3] Local application/library specific imports
import interface
import database

# Initialize bot and dispatcher
config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
TOKEN = config["Telegram"]["TOKEN"] # обращаемся как к обычному словарю!
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """This handler will be called when user sends /start"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    #проверим есть ли пользователь в базе
    row = database.cur.fetchone()
    database.cur.execute('SELECT * FROM Users WHERE id = ?',(user_id,))
    database.conn.commit()
    if row is None:
        database.cur.execute('INSERT INTO Users (id, user_name) VALUES (?, ?)',(user_id, first_name))#update status 1 when it will be deployed
        database.conn.commit()
        await bot.send_message(message.from_user.id, "Вы были записаны базу данных")
    else:
        print("Пользователь " + first_name + " вошел")
    await message.reply("Привет!\nНапиши мне что-нибудь!",reply_markup=main_menu)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    """This handler will be called when user sends /help"""
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler()
async def echo_message(message: types.Message):
    """This handler will be called when user sends any other command"""
    user_id = message.from_user.id

    if message.text == 'Музыка':
        #проверим есть ли ссылка на плейлист для этого пользователя
        database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
        row = database.cur.fetchone()
        database.conn.commit()
        if row is None:
            await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
        else:
            await bot.send_message(message.from_user.id, "Плейлист найден url = " + str(row[0]))
            await message.reply("Выберите действие",reply_markup=music_menu)

    elif message.text == 'Скачать':
        #условие на то то файлы уже есть в папке и ожидают юзера сваленные по причине ошибки
        #заменить блок функцией
        userdirectory = 'files/users/' + str(message.from_user.id)

        try:
            os.listdir(userdirectory)
        except FileNotFoundError:
            os.mkdir(userdirectory)
        except:
            print("[Error] can't create file, access denied may be for the folder")

        for f in os.listdir(userdirectory):
            if '.mp3' in f:
                audio = open(userdirectory + '/' + f, 'rb')
                pattern = '[^\.]*'
                m = re.search(pattern,f)
                filename = m.group(0)

                try:
                    await bot.send_audio(message.from_user.id, audio, performer = filename, title = filename)
                    audio.close()
                    os.remove(userdirectory + '/' + f)
                except ConnectionResetError as ECONNRESET:
                    print("Произошел разрыв соединения с пользователем " + str(message.from_user.id))
                except Exception as err:
                    print("[Exception]" + traceback.format_exc())
        #
        database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
        row = database.cur.fetchone()
        database.conn.commit()
        if row is None:
            await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
        else:
            url = str(row[0])
            await bot.send_message(message.from_user.id, "Начинается скачивание плейлиста по url = " + url)
            link = Playlist(url)
            try:
                os.chdir(userdirectory)
            except FileNotFoundError:
                os.mkdir(userdirectory)
                os.chdir(userdirectory)
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

                database.cur.execute('SELECT id FROM Playlist WHERE url = ?',(url,))
                row = database.cur.fetchone()
                database.conn.commit()
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
                        m = re.search(pattern,url)

                        downloadedtile = video_title + '-' + m.group(1) + '.' + options['postprocessors'][0]['preferredcodec']
                        filename = video_title + '.' + options['postprocessors'][0]['preferredcodec']
                        try:
                            os.rename(downloadedtile, filename)
                        except OSError:
                            print("[WinError 123] Синтаксическая ошибка в имени файла, имени папки или метке тома:")
                            filename = downloadedtile
                        print("filename " + filename)

                        database.cur.execute('INSERT INTO Playlist (user_id, url, status) VALUES (?, ?, ?)',(message.from_user.id, url, STATUS_CODE_JUST_DOWNLOADED))#update status 1 when it will be deployed
                        database.conn.commit()
                        #заменить блок функцией
                        try:
                            audio = open(filename, 'rb')
                        except:
                            print("Не удается открыть файл " + filename)
                            continue
                        try:
                            await bot.send_audio(message.from_user.id, audio, performer = video_title, title = video_title)
                            audio.close()
                            os.remove(filename)
                        except ConnectionResetError as ECONNRESET:
                            print("Произошел разрыв соединения с пользователем " + str(message.from_user.id))
                        except Exception as err:
                            print("[Exception]" + traceback.format_exc())

            if count == 0:
                await bot.send_message(message.from_user.id, "Новых саундтреков нет")
            else:
                await bot.send_message(message.from_user.id, "Добавлено " + str(count) + " саундтрек(ов)")

    elif message.text == 'Редактировать плейлист':
        await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
    else:
        if '.com/playlist?list' in message.text:
            link = message.text
            database.cur.execute('UPDATE Users SET playlist_url = ? WHERE id = ?',(link,user_id))
            row = database.cur.fetchone()
            database.conn.commit()
            await bot.send_message(message.from_user.id, "Ссылка была успешно добавлена " + link)
        else:
            await bot.send_message(message.from_user.id, message.text)

if __name__ == '__main__':

    STATUS_CODE_JUST_DOWNLOADED = 0
    path = os.path.abspath("files/")
    os.environ["PATH"] += os.pathsep + path

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    database.makedb()
    interface.createbuttons()
    executor.start_polling(dp)
