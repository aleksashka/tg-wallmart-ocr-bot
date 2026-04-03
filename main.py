import asyncio
import warnings

from aiogram import Bot, Dispatcher

import credentials
from handlers import photos


warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true")


async def main():
    bot = Bot(token=credentials.TG_TOKEN)
    dp = Dispatcher()

    dp.include_router(photos.router)
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
