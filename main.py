import asyncio
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
import logging

from handlers import router
from database.models import async_main

load_dotenv()

token = os.getenv('TOKEN')
bot = Bot(token=token)
dp = Dispatcher()



async def main(dp):
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main(dp))
    except KeyboardInterrupt:
        print('Выключение...')