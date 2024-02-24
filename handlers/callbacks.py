from random import randint
import sqlite3
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram import Router, F, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ujson import loads, load
from requests import get

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from common import menus
from keyboards import inline, reply

router = Router()

class AddHost(StatesGroup):
     domain = State()
     address = State()
class MenuCallback(CallbackData, prefix='menus'):
    menu: str
    button: str

@router.callback_query(MenuCallback.filter(F.menu == "main"))
async def callback(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
     chat_id = query.message.chat.id
     if callback_data.button == 'evr_price':
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        
        api_url = 'https://api.evernode.network/market/info'
        api_req = get(api_url)
        data = loads(api_req.text)

        evr_price = data['data']['currentPrice']
        evr_increase = float(data['data']['increase'])

        emoji = ''
        if evr_increase > 0: 
             emoji = '🟢'
        elif evr_increase < 0:
             emoji = '🔴'
        else:
             emoji = '🟡'

        return_kb = inline.get_keyboard(
             "Return",
             btns_callback=(MenuCallback(menu='price_menu', button='return_main_menu')),
             btns_url=(None)
        ).as_markup()

        await bot.send_message(chat_id=query.message.chat.id, text=f'Current price of EVR: <b>{evr_price}$</b>\nEvr\'s increase: <b>{evr_increase}</b>% {emoji}', 
                           parse_mode='html', 
                           reply_markup=return_kb
                           )
     elif callback_data.button == 'hosts':
          await bot.delete_message(chat_id, query.message.message_id)

          hosts_main_kb = menus.hosts_menu()

          await bot.send_message(chat_id, f'Choose which hosts\' statistics you want to see.', reply_markup=hosts_main_kb)

@router.callback_query(MenuCallback.filter(F.menu.in_(['hosts', 'price_menu'])))
async def return_main_menu(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
     chat_id = query.message.chat.id
     if callback_data.button == 'return_main_menu':
          await bot.delete_message(query.message.chat.id, query.message.message_id)
          main_kb = inline.get_keyboard(
               "EVR Price",
               "Hosts",
               btns_callback=(MenuCallback(menu="main", button="evr_price"), MenuCallback(menu="main", button="hosts")),
               btns_url=(None, None)
               ).as_markup()

          await bot.send_message(chat_id=query.message.chat.id, 
                                 text=f'Welcome, {query.from_user.first_name}! \nDeveloper - Michael Kloster (@mihai_toster). Where do you want to start?', 
                                 reply_markup=main_kb)
     elif callback_data.button == 'all_hosts':
          await bot.delete_message(chat_id, query.message.message_id)

          api_url = f'https://api.evernode.network/support/stats'
          api_req = get(api_url)
          data = loads(api_req.text)

          hosts = data['hosts']
          active = data['active']
          inactive = data['inactive']

          return_kb = inline.get_keyboard(
               "Return",
               btns_callback=(MenuCallback(menu='all_hosts', button='return_hosts_menu')),
               btns_url=(None)
          ).as_markup()

          await bot.send_message(chat_id, 
                           f'Number of <u>all</u> hosts - <b>{hosts}</b> ⚪\nNumber of <u>active</u> hosts - <b>{active} 🟢</b>\nNumber of <u>inactive</u> hosts - <b>{inactive} 🔴</b>', 
                           parse_mode='html', 
                           reply_markup=return_kb)
     elif callback_data.button == 'my_hosts':
          await bot.delete_message(chat_id, query.message.message_id)
          
          my_hosts_kb, count_hosts = menus.my_hosts(query.from_user.id)
          my_hosts_kb = my_hosts_kb.as_markup()
          await bot.send_message(chat_id, 
                                 text=f"Now you have <u><b>{count_hosts}</b></u> hosts in your list, but you can add more at any time.",
                                 parse_mode="HTML",
                                 reply_markup=my_hosts_kb
                                 )

@router.callback_query(MenuCallback.filter(F.menu.in_(['all_hosts', 'my_hosts'])))
async def return_main_menu(query: CallbackQuery, callback_data: CallbackData, bot: Bot, state: FSMContext):
     chat_id = query.message.chat.id
     if callback_data.button == 'return_hosts_menu':
          await bot.delete_message(chat_id, query.message.message_id)

          hosts_main_kb = menus.hosts_menu()

          await bot.send_message(chat_id, f'Choose which hosts\' statistics you want to see.', reply_markup=hosts_main_kb)
     elif callback_data.button == 'add_host':
          await bot.delete_message(chat_id, query.message.message_id)

          file_domains = open('data\domains.json')
          data = load(file_domains)

          await state.set_state(AddHost.domain)

          domains_kb = reply.get_keyboard(
               data[randint(0, len(data)-1)],
               data[randint(0, len(data)-1)],
               data[randint(0, len(data)-1)],
               data[randint(0, len(data)-1)],
               "Cancel",
               sizes=(2, 2, 2, 1, )
          ).as_markup(
               resize_keyboard=True,
               input_field_placeholder='Please send\choose Top-Level Domain',
               one_time_keyboard=True
          )

          await bot.send_message(chat_id, 
                                 text="Please send\choose Top-Level Domain. Here are some of the domains", 
                                 reply_markup=domains_kb)
     elif callback_data.button == 'delete_host':
          await bot.delete_message(query.message.chat.id, query.message.message_id)

          db = sqlite3.connect('data\sqlite.db')
          cursor = db.cursor()

          cursor.execute(f"SELECT address FROM hosts WHERE user_telegram_id = {query.from_user.id}")
          addresses = cursor.fetchall()

          keyboard = InlineKeyboardBuilder()

          for i in addresses:
               keyboard.button(
                    text=i[0],
                    callback_data=MenuCallback(menu='delete', button=f'delete_host_pre.{i[0]}')
               )
          keyboard.button(text="Return", callback_data=MenuCallback(menu='stats', button='return_my_hosts_menu'))
          keyboard = keyboard.adjust(*[1] * len(addresses), 1).as_markup()

          await bot.send_message(chat_id, 
                                 text='Choose which address you want to delete. Here are all your addresses',
                                 parse_mode="HTML",
                                 reply_markup=keyboard
                                 )
     elif callback_data.button[:5] == 'stats':
          await bot.delete_message(chat_id, query.message.message_id)

          db = sqlite3.connect('data\sqlite.db')
          cursor = db.cursor()

          address = callback_data.button.split('.')[-1:][0]

          cursor.execute(f"SELECT domain_tld FROM hosts WHERE address = '{address}'")
          domain = cursor.fetchone()[0]

          api_url = f'https://api.evernode.network/registry/hosts/{domain}?limit=1000'
          api_req = get(api_url)
          data = loads(api_req.text)
          data = data['data']

          for i in data:
               address_i = i['address']
               if address == address_i:
                    country_code = i['countryCode']
                    email = i['email']
                    maxInstances = i['maxInstances']
                    activeInstances = i['activeInstances']
                    version = i['version']
                    cpuModelName = i['cpuModelName']
                    cpuCount = i['cpuCount']
                    ramMb = i['ramMb']
                    diskMb = i['diskMb']
                    accumulatedRewardAmount = i['accumulatedRewardAmount']
                    addressBalance = i['addressBalance']

                    return_kb = inline.get_keyboard(
                         "Return",
                         btns_callback=(MenuCallback(menu='stats', button='return_my_hosts_menu')),
                         btns_url=(None)
                    ).as_markup()

                    await bot.send_message(query.message.chat.id, 
                                           text=f'Here are statistics for this address:\nAddress - <b>{address}</b>\nDomain - {domain}\nEmail - {email}\nCountry code - {country_code}\nMax instances - <u><b>{maxInstances}</b></u> ⚪\nActive instances - <u><b>{activeInstances}</b></u> 🟢\nVersion - {version}\nCpu model name - {cpuModelName}\n- Machine\'s pecifications:\n    Ram - <u><b>{round(int(ramMb) / 1024, 1)}</b></u> (GB)\n    Disk - <u><b>{round(int(diskMb) / 1024, 1)}</b></u> (GB)\n    Cpu cores - <u><b>{cpuCount}</b></u>\nAccumulated reward amount - {round(float(accumulatedRewardAmount), 3)} EVR\nAddress balance - {round(float(addressBalance), 3)} EVR',
                                           parse_mode="HTML",
                                           reply_markup=return_kb
                                           )

                    break

@router.callback_query(MenuCallback.filter(F.menu.in_(['delete'])))
async def return_main_menu(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
     chat_id = query.message.chat.id
     if callback_data.button[:len("delete_host_pre")] == 'delete_host_pre':
          address = callback_data.button.split('.')[-1:][0]
          await bot.delete_message(chat_id, query.message.message_id)

          keyboard = inline.get_keyboard(
               "Confirm",
               btns_callback=(MenuCallback(menu='delete', button=f'confirm.{address}')),
               btns_url=None
          )

          await bot.send_message(chat_id, 
                                 text=f'Confirm that you want to delete this particular address: <b>{address}</b>',
                                 parse_mode="HTML",
                                 reply_markup=keyboard.as_markup()
                                 )
     elif callback_data.button[:len('confirm')] == 'confirm':
          address = callback_data.button.split('.')[-1:][0 ]

          await bot.delete_message(chat_id, query.message.message_id)
          db = sqlite3.connect('data\sqlite.db')
          cursor = db.cursor()

          cursor.execute(f"DELETE FROM hosts WHERE user_telegram_id = {query.from_user.id} AND address = '{address}'")
          db.commit()

          cursor.execute(f"SELECT count_hosts FROM users WHERE user_telegram_id = {query.from_user.id}")
          count_hosts = cursor.fetchone()[0]
          cursor.execute(f"UPDATE users SET count_hosts = {count_hosts-1}")
          db.commit()

          my_hosts_kb, count_hosts = menus.my_hosts(query.from_user.id)

          await bot.send_message(chat_id, 
                           text='Address was deleted successfully',
                           parse_mode="HTML"
                           )
          
          my_hosts_kb = my_hosts_kb.as_markup()

          await bot.send_message(chat_id=query.message.chat.id, text=f"Now you have <u><b>{count_hosts}</b></u> hosts in your list, but you can add more at any time.",
                              parse_mode="HTML", 
                              reply_markup=my_hosts_kb
                              )


@router.callback_query(MenuCallback.filter(F.menu.in_(['stats', 'delete'])))
async def return_main_menu(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
     if callback_data.button == 'return_my_hosts_menu':
          await bot.delete_message(query.message.chat.id, query.message.message_id)

          my_hosts_kb, count_hosts = menus.my_hosts(query.from_user.id)
          my_hosts_kb = my_hosts_kb.as_markup()

          await bot.send_message(chat_id=query.message.chat.id, text=f"Now you have <u><b>{count_hosts}</b></u> hosts in your list, but you can add more at any time.",
                              parse_mode="HTML", 
                              reply_markup=my_hosts_kb
                              )
          