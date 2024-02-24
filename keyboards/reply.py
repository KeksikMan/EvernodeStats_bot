from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

def get_keyboard(
        *btns_names: str,
        sizes: tuple[int] = (2, ),
):
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns_names, start=0):
        keyboard.button(text=text) 

    return keyboard.adjust(*sizes)


delete_kb = ReplyKeyboardRemove()