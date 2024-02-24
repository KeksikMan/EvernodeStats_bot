import sqlite3

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import inline

from handlers import callbacks

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    db = sqlite3.connect('data\sqlite.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_name TEXT,
                   user_telegram_id BIGINT,
                   count_hosts INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS hosts (
                   id INTEGER,
                   user_telegram_id,
                   address TEXT,
                   key TEXT,
                   domain_tld TEXT,
                   country_code TEXT,
                   email TEXT
    )""")
    db.commit()

    cursor.execute(f"SELECT user_telegram_id FROM users WHERE user_telegram_id = '{message.from_user.id}'")
    if cursor.fetchone() is None: 
        cursor.execute(f"INSERT INTO users (user_name, user_telegram_id, count_hosts) VALUES (?, ?, ?)", (message.from_user.username, message.from_user.id, 0))
    db.commit()

    main_kb = inline.get_keyboard(
        "EVR Price",
        "Hosts",
        btns_callback=(callbacks.MenuCallback(menu="main", button="evr_price"), callbacks.MenuCallback(menu="main", button="hosts")),
        btns_url=(None, None)
    ).as_markup()

    await message.answer(text=f'Welcome, {message.from_user.first_name}! \nDeveloper - Michael Kloster (@mihai_toster). Where do you want to start?', reply_markup=main_kb)

    db.close()