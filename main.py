import os
import logging
from utils.logging_config import configure_logging
configure_logging()
from aiogram import executor
from bot import dp
from utils import database, buttons

import handlers.commands
import handlers.echo

if __name__ == '__main__':
    path = os.path.abspath("files/")
    os.environ["PATH"] += os.pathsep + path

    logging.basicConfig(level=logging.DEBUG, filename = "files/logs.log", filemode="w")

    database.makedb()
    buttons.createbuttons()

    executor.start_polling(dp)