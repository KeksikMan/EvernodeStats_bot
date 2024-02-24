import config, asyncio

from threading import Thread

from aiogram import Bot, Dispatcher

from common import domains_reload
from commands import start_command
from handlers import callbacks, messages
from aiogram.fsm.strategy import FSMStrategy

async def main():
    token = config.TOKEN
    bot = Bot(token)
    dp = Dispatcher(FSMStrategy = FSMStrategy.USER_IN_CHAT)

    task_reload_domains = Thread(target=domains_reload.reload_domain_info)
    task_reload_domains.start()

    dp.include_router(start_command.router)
    dp.include_router(callbacks.router)
    dp.include_router(messages.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")