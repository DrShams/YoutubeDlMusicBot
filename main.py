import os
import logging
import asyncio

from bot import dp, bot
from utils import database, buttons
from utils.logging_config import configure_logging

from handlers.commands import router as commands_router
from handlers.echo import router as echo_router

dp.include_router(commands_router)
dp.include_router(echo_router)

configure_logging()

async def main():
    path = os.path.abspath("files/")
    os.environ["PATH"] += os.pathsep + path

    database.makedb()
    buttons.createbuttons()

    print("started")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt as exception:
        logging.warning("You stopped the execution of the programm")

if __name__ == '__main__':
    asyncio.run(main())