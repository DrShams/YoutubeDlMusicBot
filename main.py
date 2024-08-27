import os
import logging
from aiogram import executor

from bot import dp
from utils import database, buttons
from utils.logging_config import configure_logging

configure_logging()

import handlers.commands
import handlers.echo

if __name__ == '__main__':
    path = os.path.abspath("files/")
    os.environ["PATH"] += os.pathsep + path

    database.makedb()
    buttons.createbuttons()
    try:
        print("started")
        executor.start_polling(dp)
    except KeyboardInterrupt as exception:
        logging.warning("You stopped the execution of the programm")