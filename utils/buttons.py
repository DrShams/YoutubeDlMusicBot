from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def createbuttons():
    """Create buttons for telegram bot"""

    btn_music_download = KeyboardButton('Скачать')
    btn_music_change = KeyboardButton('Редактировать плейлист')

    main_menu = ReplyKeyboardMarkup(resize_keyboard = True) # чтобы кнопки не были во весь экран
    main_menu.add(btn_music_download, btn_music_change)

    return main_menu