from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import configparser  # импортируем библиотеку
config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
TOKEN = config["Telegram"]["TOKEN"] # обращаемся как к обычному словарю!
print(TOKEN)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
print(bot)
