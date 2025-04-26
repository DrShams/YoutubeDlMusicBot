from aiogram import Bot, Dispatcher
import configparser

# Initialize bot and dispatcher
config = configparser.ConfigParser()  # создаём объекта парсера
config.read("files/settings.ini")  # читаем конфиг
TOKEN = config["Telegram"]["TOKEN"] # обращаемся как к обычному словарю!
bot = Bot(token=TOKEN)
dp = Dispatcher()