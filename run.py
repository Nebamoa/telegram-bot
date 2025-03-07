import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers import router, check_and_notify
from database.models import async_main


async def main():
    await async_main()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    asyncio.create_task(check_and_notify())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
