import logging

from aiogram import types, Router
from aiogram.filters import Command

from bot import bot
from utils import database
from utils.buttons import createbuttons
from utils.logging_config import configure_logging



configure_logging()
main_menu = createbuttons()
router = Router()

@router.message(Command("start"))
async def process_start_command(message: types.Message):
    """This handler will be called when user sends /start"""

    user_id = message.from_user.id
    first_name = message.from_user.first_name

    database.cur.execute('SELECT * FROM Users WHERE id = ?',(user_id,))
    row = database.cur.fetchone()

    if row is None:
        database.cur.execute('INSERT INTO Users (id, user_name) VALUES (?, ?)',(user_id, first_name))#update status 1 when it will be deployed
        database.conn.commit()
        await bot.send_message(message.from_user.id, "Вы были записаны базу данных")
    else:
        logging.info("User " + first_name + " entered")
    
    database.cur.execute('SELECT playlist_url FROM Users WHERE id = ?',(user_id,))
    playlist_row = database.cur.fetchone()
    if playlist_row is None or not playlist_row[0]:
        await send_welcome_message(message)
    else:
        database.cur.execute('SELECT count(*) FROM PlayList WHERE user_id = ? AND status = 0', (user_id,))
        count_row = database.cur.fetchone()
        track_count = count_row[0] if count_row else 0
        await send_message_with_residual_tracks_to_download(message, track_count)
    

@router.message(Command("help"))
async def process_help_command(message: types.Message):
    """This handler will be called when user sends /help"""

    await send_welcome_message(message)

async def send_welcome_message(message: types.Message):
    await message.reply(
        "Привет, это музыкальный бот позволяющий скачивать трэки с Youtube к вам в телефон\n"
        "Зайди в Youtube и перейди к своему PlayList\n"
        "Скопируй ссылку и вставь URL сюда, в будущем тебе нужно будет только нажимать кнопку [Скачать]",
        reply_markup=main_menu
    )
async def send_message_with_residual_tracks_to_download(message: types.Message, tracks: int):
    await message.reply(
        f"Привет, в твоем плейлисте +{tracks} треков\n"
        "Нажми на кнопку [Скачать]",
        reply_markup=main_menu
    )