import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from database.models import User
from database.db import init_db
from database.db import SessionLocal
from sqlalchemy import select

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    async with SessionLocal() as session:
        query = select(User).where(User.telegram_id == telegram_id) 
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            new_user = User(
                telegram_id= telegram_id ,
                username= username,
                first_name= first_name
            )
            session.add(new_user)
            await session.commit()

            await message.answer("Привет! Я сохранил тебя в базе.")
        
        else:
            await message.answer("Привет! Ты уже есть в базе.")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())