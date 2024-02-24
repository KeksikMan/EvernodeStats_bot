import sqlite3
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers.callbacks import AddHost
from aiogram.filters import StateFilter

from ujson import load, loads
from requests import get

from keyboards import reply

from common import menus

router = Router()

@router.message(Command("start"))
@router.message(Command("cancel"))
@router.message(F.text == "Cancel")
async def cancel(message: Message, bot: Bot, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return
    
    await message.answer("Canceled successfully!", reply_markup=reply.delete_kb)
    await state.clear()

    my_hosts_kb, count_hosts = menus.my_hosts(message.from_user.id)
    my_hosts_kb = my_hosts_kb.as_markup()

    await message.answer(text=f"Now you have <u><b>{count_hosts}</b></u> hosts in your list, but you can add more at any time.",
                        parse_mode="HTML", 
                        reply_markup=my_hosts_kb
                        )

@router.message(AddHost.domain, F.text)
async def choose_domain(message: Message, state: FSMContext, bot: Bot):
    file = open("data\domains.json")
    domains = load(file)
    if message.text in domains:
        await state.update_data(domain=message.text)
        
        domain = await state.get_data()
        domain = domain['domain']
        api_url = f'https://api.evernode.network/registry/hosts/{domain}?limit=3'
        api_req = get(api_url)
        data = loads(api_req.text)
        data = data['data']
        if len(data) == 0:
            await bot.send_message(message.chat.id, "Sorry, but domain doesn\'t have any addresses. Write/choose domain again or press \'cancel\'")
        else:
            addresses_kb = ReplyKeyboardBuilder()
            for i in data[:3]:
                address = i['address']
                addresses_kb.button(text=address)
            addresses_kb.button(text='Cancel')
            addresses_kb = addresses_kb.adjust(1, 1, 1, 1).as_markup(
                resize_keyboard=True,
                input_field_placeholder='Please send\choose address of this domain',
                one_time_keyboard=True
            )
            await bot.send_message(message.chat.id,
                                "Thank you, now send me an address you want to add. Here are some of addresses of this domain", 
                                reply_markup=addresses_kb)
            await state.set_state(AddHost.address)
    else:
        await bot.send_message(message.chat.id, "Sorry, but domain is incorrect. Write/choose domain again or press \'cancel\'")

@router.message(AddHost.address, F.text)
async def choose_address(message: Message, state: FSMContext, bot: Bot):
    domain = await state.get_data()
    domain = domain['domain']
    api_url = f'https://api.evernode.network/registry/hosts/{domain}?limit=1000'
    api_req = get(api_url)
    data = loads(api_req.text)
    data = data['data']

    msg_address = message.text.strip()
    address_existence = False

    for i in data:
        address = i['address']
        if address == msg_address:
            await state.update_data(address=message.text)
            address_existence = True
            
            db = sqlite3.connect('data\sqlite.db')
            cursor = db.cursor()

            country_code = i['countryCode']
            key = i['key']
            email = i['email']

            cursor.execute(f"SELECT address FROM hosts WHERE user_telegram_id = {message.from_user.id}")
            isAlreadyHave_list = cursor.fetchall()
            g = False
            if isAlreadyHave_list != None :
                for b in isAlreadyHave_list:
                    if b[0] == address:
                        await message.answer("Sorry, but you can\'t add this address as you\'ve already added it.")
                        g = True
                        break
            if g: break
            cursor.execute(f"SELECT id FROM users WHERE user_telegram_id = '{message.from_user.id}'")
            id = cursor.fetchone()[0]

            cursor.execute(f"INSERT INTO hosts (id, user_telegram_id, address, key, domain_tld, country_code, email) VALUES (?, ?, ?, ?, ?, ?, ?)", (id, message.from_user.id, address, key, domain, country_code, email))
            db.commit()

            cursor.execute(f"SELECT count_hosts FROM users WHERE user_telegram_id = {message.from_user.id}")
            count_host = cursor.fetchone()[0]
            cursor.execute(f"UPDATE users SET count_hosts = {1 + count_host} WHERE user_telegram_id = '{message.from_user.id}'")
            db.commit()

            await message.answer("Address was <b>successfully</b> added, now you can check it.",
                                parse_mode="HTML",
                                reply_markup=reply.delete_kb
                                )
            
            my_hosts_kb, count_hosts = menus.my_hosts(message.from_user.id)
            my_hosts_kb = my_hosts_kb.as_markup()

            break
    if not address_existence:
        await message.answer("Sorry, but this address was not found, try again or press \'cancel\'")
    else:
        my_hosts_kb, count_hosts = menus.my_hosts(message.from_user.id)
        my_hosts_kb = my_hosts_kb.as_markup()
        await message.answer(text=f"Now you have <u><b>{count_hosts}</b></u> hosts in your list, but you can add more at any time.",
                                parse_mode="HTML",
                                reply_markup=my_hosts_kb
                                )
        
        await state.clear()