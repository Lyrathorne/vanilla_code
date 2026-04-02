import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from sqlalchemy import select

from database.models import User, Task
from database.db import init_db, SessionLocal
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/tasks"), KeyboardButton(text="/add")],
        [KeyboardButton(text="/done")]
    ],
    resize_keyboard=True
)

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
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            session.add(new_user)
            await session.commit()

            await message.answer(
                "Привет! Я сохранил тебя в базе.",
                reply_markup=main_keyboard
            )
        else:
            await message.answer(
                "Привет! Ты уже есть в базе.",
                reply_markup=main_keyboard
            )

@dp.message(Command("add"))
async def add_handler(message: Message):
    telegram_id = message.from_user.id
    text = message.text.replace("/add", "", 1).strip()

    if not text:
        await message.answer("Напиши задачу после /add")
        return

    async with SessionLocal() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start")
            return

        new_task = Task(
            creator_id=user.id,
            text=text,
            status=False
        )
        session.add(new_task)
        await session.commit()

    await message.answer("Задача добавлена")

@dp.message(Command("tasks"))
async def tasks_handler(message: Message):
    telegram_id = message.from_user.id

    async with SessionLocal() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start")
            return

        tasks_query = select(Task).where(Task.creator_id == user.id)
        tasks_result = await session.execute(tasks_query)
        tasks = tasks_result.scalars().all()

        if not tasks:
            await message.answer("У тебя пока нет задач 📭")
            return

        for index, task in enumerate(tasks, start=1):
            status_icon = "✅" if task.status else "❌"

            if not task.status:
                inline_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Выполнить",
                                callback_data=f"done_{task.id}"
                            )
                        ]
                    ]
                )

                await message.answer(
                    f"{index}. {status_icon} {task.text}",
                    reply_markup=inline_kb
                )
            else:
                await message.answer(
                    f"{index}. {status_icon} {task.text}"
                )

@dp.message(Command("done"))
async def done_handler(message: Message):
    telegram_id = message.from_user.id
    text = message.text.replace("/done", "", 1).strip()

    if not text.isdigit():
        await message.answer("Напиши номер задачи: /done 1")
        return

    task_number = int(text)

    async with SessionLocal() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start")
            return

        tasks_query = select(Task).where(Task.creator_id == user.id)
        tasks_result = await session.execute(tasks_query)
        tasks = tasks_result.scalars().all()

        if not tasks:
            await message.answer("У тебя нет задач")
            return

        if task_number < 1 or task_number > len(tasks):
            await message.answer("Неверный номер задачи")
            return

        task = tasks[task_number - 1]
        task.status = True
        await session.commit()

    await message.answer(f"Задача {task_number} выполнена ✅")

@dp.callback_query(lambda callback: callback.data.startswith("done_"))
async def done_task_callback(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id

    async with SessionLocal() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user is None:
            await callback.answer("Сначала используй /start", show_alert=True)
            return

        task_query = select(Task).where(
            Task.id == task_id,
            Task.creator_id == user.id
        )
        task_result = await session.execute(task_query)
        task = task_result.scalar_one_or_none()

        if task is None:
            await callback.answer("Задача не найдена", show_alert=True)
            return

        task.status = True
        await session.commit()

    new_text = callback.message.text.replace("❌", "✅", 1)
    await callback.message.edit_text(new_text)
    await callback.answer("Задача отмечена как выполненная ✅")

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())