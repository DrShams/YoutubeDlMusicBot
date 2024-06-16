from aiogram import types
from bot import bot, dp
from utils import database
import logging

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """This handler will be called when user sends /start"""

    user_id = message.from_user.id
    first_name = message.from_user.first_name

    database.cur.execute('SELECT * FROM Users WHERE id = ?',(user_id,))
    row = database.cur.fetchone()
    
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