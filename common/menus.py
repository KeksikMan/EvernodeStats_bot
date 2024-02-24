import sqlite3
from keyboards import inline
from aiogram.utils.keyboard import InlineKeyboardBuilder

def hosts_menu():
     hosts_main_kb = inline.get_keyboard(
          "All hosts",
          "My hosts",
          "Return",
          btns_callback=(inline.MenuCallback(menu='hosts', button='all_hosts'), 
                         inline.MenuCallback(menu='hosts', button='my_hosts'),
                         inline.MenuCallback(menu='hosts', button='return_main_menu')
                         ),
          btns_url=(None, None, None)
     ).as_markup()

     return hosts_main_kb

def my_hosts(user_id):
     db = sqlite3.connect('data\sqlite.db')
     cursor = db.cursor()

     cursor.execute(f"SELECT count_hosts FROM users WHERE user_telegram_id = '{user_id}'")
     count_hosts = cursor.fetchone()[0]

     my_hosts_kb = InlineKeyboardBuilder()
     
     if count_hosts > 0:
          cursor.execute(f"SELECT id FROM users WHERE user_telegram_id = '{user_id}'")
          id = cursor.fetchone()[0]
          
          for i in cursor.execute(f"SELECT address FROM hosts WHERE id = {id}"):
               my_hosts_kb.button(text=i[0], callback_data=inline.MenuCallback(menu='my_hosts', button=f'stats.{i[0]}'))

          
          my_hosts_kb.button(text='Add host', callback_data=inline.MenuCallback(menu='my_hosts', button='add_host'))
          my_hosts_kb.button(text='Delete host', callback_data=inline.MenuCallback(menu='my_hosts', button='delete_host'))
     else:
          my_hosts_kb.button(text='Add host', callback_data=inline.MenuCallback(menu='my_hosts', button='add_host'))

     my_hosts_kb.button(text='Return', callback_data=inline.MenuCallback(menu='my_hosts', button='return_hosts_menu'))
     db.close()
     my_hosts_kb.adjust(*[1] * count_hosts, 2, 1)

     return my_hosts_kb, count_hosts