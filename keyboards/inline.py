from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callbacks import MenuCallback

def get_keyboard(
        *btns_names: str,
        btns_callback: tuple[MenuCallback],
        btns_url: tuple[str] = (None, ),
):
    '''
    Exemple:
    def get_keyboard(
        "Menu",
        "Hosts",
        "Close",
        btns_callback=(MenuCallback(menu='main', button='Hosts', MenuCallback(menu='main', button='Close', ...),
        btns_url=(None, None, None),
    )
    '''
    keyboard = InlineKeyboardBuilder()

    for index, text in enumerate(btns_names, start=0):
        if btns_url is None:
            keyboard.button(text=text, 
                callback_data=btns_callback
                )
        elif btns_url[index] == None:
            keyboard.button(text=text, 
                            callback_data=btns_callback[index]
                            )
        else:
            keyboard.button(text=text, 
                            callback_data=btns_callback[index], 
                            url=btns_url[index]
                            )

    return keyboard.adjust(2, 2, 2, 2)