#[1]Standard library imports
import os
import re
import configparser
import logging

#[2]Related third party imports.
import traceback
from aiogram import Bot, Dispatcher, executor, types
from pytube import Playlist

#[3] Local application/library specific imports
import interface
import database
import youtube

# Initialize bot and dispatcher
config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
TOKEN = config["Telegram"]["TOKEN"] # обращаемся как к обычному словарю!
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def send_audio(message: types.Message, filename):
    """Send audiofile to the user"""

    pattern = '[^\.]*'
    m = re.search(pattern,filename)
    track_title = m.group(0)

    filenamepath = 'files/users/' + str(message.from_user.id) + '/' + filename
    try:
        audio = open(filenamepath, 'rb')
        logging.debug("file " + filenamepath + " successfully open")
    except:
        logging.warning("file " + filename + " couldn't open")
        return False
    try:
        await bot.send_audio(message.from_user.id, audio, performer = track_title, title = track_title)#change performer
        logging.info("the file " + filenamepath + " sucessefully sent to " + message.from_user.first_name)
        audio.close()
        os.remove(filenamepath)
        logging.debug("the file " +  filenamepath + " removed")
    except ConnectionResetError as ECONNRESET:
        logging.warning("[ConnectionResetError]Connection with the user " + message.from_user.first_name + " has been interrupted")
    except Exception as err:
        logging.warning("[Exception]" + traceback.format_exc())

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
        logging.info("User " + first_name + " entered")
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
        logging.info("user " + message.from_user.first_name + " clicked 'Download' button")
        #заменить блок функцией
        userdirectory = 'files/users/' + str(message.from_user.id)
        if os.path.isdir(userdirectory):
            logging.debug("the folder " + userdirectory + " has been already exists")
        else:
            logging.info("the folder " + userdirectory + " created")
            os.mkdir(userdirectory)

        for filename in os.listdir(userdirectory):
            if '.mp3' in filename:
                await bot.send_message(message.from_user.id, "Ожидается отправка " + filename + " из хранилища...") #указать количество
                await send_audio(message, filename)
                logging.info("filename " + filename + " sent")

        database.cur.execute('SELECT playlist_url FROM Users WHERE id = ? AND playlist_url is not NULL',(user_id,))
        row = database.cur.fetchone()
        database.conn.commit()
        if row is None:
            await bot.send_message(message.from_user.id, "Вставьте ссылку в чат на плейлист youtube")
        else:
            url = str(row[0])
            await bot.send_message(message.from_user.id, "Начинается скачивание плейлиста по url = " + url)
            link = Playlist(url)

            count = 0
            for url in link.video_urls:
                database.cur.execute('SELECT id FROM Playlist WHERE url = ?',(url,))

                row = database.cur.fetchone()
                database.conn.commit()
                if row is None:
                    #try:
                    logging.info("downloading the file from url " + url)
                    try:
                        result = youtube.downloadfile(url)
                        logging.info("type of file " + type(result))
                        logging.info("the file from " + url + " downloaded")
                    except:
                        logging.warning("Проблема с соединением при скачивании файла " + url)
                        executor.start_polling(dp)#DELETE?
                        logging.info("Соединение было перезапущено")

                    if result != 'NONE':
                        count = count + 1
                        if 'entries' in result: # Can be a playlist or a list of videos
                            video = result['entries'][0]
                        else:  # Just a video
                            video = result
                        video_title = video['title']

                        pattern = '=([\w\-\/]*)'
                        m = re.search(pattern,url)
                        
                        downloadedtile = video_title + '-' + m.group(1) + '.mp3'
                        filename = video_title + '.mp3'
                        filesize = os.stat(downloadedtile).st_size / (1024*1024)#megabytes
                        if filesize < 50:
                            try:
                                pathto = os.getcwd() + '/files/users/' + str(message.from_user.id)+ '/' + filename
                                os.rename(downloadedtile, pathto)
                                logging.info("the file " + downloadedtile + " renamed and replaced to " + pathto)
                            except OSError:
                                logging.warning("[OSError] Синтаксическая ошибка в имени файла, имени папки или метке тома:")
                                filename = downloadedtile
                        else:
                            logging.warning("filesize " + str(filesize) +  " was skipper (more than 50 megabytes)")

                        database.cur.execute('INSERT INTO Playlist (user_id, url, status) VALUES (?, ?, ?)',(message.from_user.id, url, STATUS_CODE_JUST_DOWNLOADED))#update status 1 when the file will be send
                        database.conn.commit()

                        await send_audio(message, filename)


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
    logging.basicConfig(level=logging.INFO, filename = "logs.log", filemode="w")

    database.makedb()
    interface.createbuttons()
    #try:
    executor.start_polling(dp)
    """except KeyboardInterrupt:
        logging.info("programm has been interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)"""
