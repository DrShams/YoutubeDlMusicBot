from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def createbuttons():
    """Create buttons for telegram bot"""

    btn_music_download = KeyboardButton(text='Скачать')
    btn_music_change = KeyboardButton(text='Редактировать плейлист')

    main_menu = ReplyKeyboardMarkup(
        keyboard=[[btn_music_download, btn_music_change]],
        resize_keyboard=True
    )
    return main_menu