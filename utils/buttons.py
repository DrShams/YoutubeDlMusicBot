from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def createbuttons():
    """Create buttons for telegram bot"""

    # --- Main Menu ---
    btn_main = KeyboardButton('Главное меню')
    btn_music = KeyboardButton('Музыка') # скачивание музыки с youtube
    btn_travel = KeyboardButton('Турагентство') # кнопка для вызова парсера для турагенства и публикации в вк
    btn_camera = KeyboardButton('Камера') # кнопка для вызова камеры
    btn_english = KeyboardButton('Английский') # кнопка для вызова парсера

    main_menu = ReplyKeyboardMarkup(resize_keyboard = True) # чтобы кнопки не были во весь экран
    main_menu.add(btn_music, btn_travel, btn_camera, btn_english, btn_main)


    # --- Full Music menu ---
    btn_music_download = KeyboardButton('Скачать')
    btn_music_change = KeyboardButton('Редактировать плейлист')
    music_menu = ReplyKeyboardMarkup(resize_keyboard = True)
    music_menu.add(btn_music_download, btn_music_change)

    # --- Shorted Music menu ---
    music_smenu = ReplyKeyboardMarkup(resize_keyboard = True)
    music_smenu.add(btn_music_change)