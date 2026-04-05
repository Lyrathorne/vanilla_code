import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.models import User, Task, format_deadline
from database.db import init_db, SessionLocal
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class AddTaskState(StatesGroup):
    waiting_for_task_text = State()
    waiting_for_deadline_choice = State()
    waiting_for_deadline_value = State()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="➕ Добавить задачу")],
        [KeyboardButton(text="📜 Архив")]
    ],
    resize_keyboard=True
)

deadline_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
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
@dp.message(lambda message: message.text == "➕ Добавить задачу")
async def add_handler(message: Message, state: FSMContext):
    await state.set_state(AddTaskState.waiting_for_task_text)
    await message.answer(
        "Напиши текст новой задачи:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(AddTaskState.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text:
        await message.answer("Текст задачи пустой. Напиши задачу ещё раз:")
        return

    await state.update_data(task_text=text)
    await state.set_state(AddTaskState.waiting_for_deadline_choice)

    await message.answer(
        "Добавить дедлайн?",
        reply_markup=deadline_choice_keyboard
    )


@dp.message(AddTaskState.waiting_for_deadline_choice)
async def process_deadline_choice(message: Message, state: FSMContext):
    choice = message.text.strip()

    if choice == "❌ Нет":
        data = await state.get_data()
        task_text = data.get("task_text")
        telegram_id = message.from_user.id

        async with SessionLocal() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if user is None:
                await message.answer("Сначала используй /start", reply_markup=main_keyboard)
                await state.clear()
                return

            new_task = Task(
                creator_id=user.id,
                text=task_text,
                status=False,
                deadline=None,
                reminded_day=False,
                reminded_hour=False,
                reminded_overdue=False
            )
            session.add(new_task)
            await session.commit()

        await state.clear()
        await message.answer("Задача добавлена ✅", reply_markup=main_keyboard)
        return

    if choice == "✅ Да":
        await state.set_state(AddTaskState.waiting_for_deadline_value)
        await message.answer(
            "Введи дедлайн в формате:\n10.04.2026 18:30",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await message.answer("Пожалуйста, выбери: ✅ Да или ❌ Нет")


@dp.message(AddTaskState.waiting_for_deadline_value)
async def process_deadline_value(message: Message, state: FSMContext):
    deadline_input = message.text.strip()

    try:
        deadline = datetime.strptime(deadline_input, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            "Неверный формат даты.\n"
            "Введи дедлайн так: 10.04.2026 18:30"
        )
        return

    if deadline <= datetime.now():
        await message.answer("Дедлайн должен быть в будущем. Введи дату ещё раз:")
        return

    data = await state.get_data()
    task_text = data.get("task_text")
    telegram_id = message.from_user.id

    async with SessionLocal() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start", reply_markup=main_keyboard)
            await state.clear()
            return

        new_task = Task(
            creator_id=user.id,
            text=task_text,
            status=False,
            deadline=deadline,
            reminded_day=False,
            reminded_hour=False,
            reminded_overdue=False
        )
        session.add(new_task)
        await session.commit()

    await state.clear()
    await message.answer("Задача с дедлайном добавлена ✅", reply_markup=main_keyboard)


@dp.message(Command("history"))
@dp.message(lambda message: message.text == "📜 Архив")
async def history_handler(message: Message):
    telegram_id = message.from_user.id

    async with SessionLocal() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start")
            return

        tasks_query = select(Task).where(
            Task.creator_id == user.id,
            Task.status == True
        )
        tasks_result = await session.execute(tasks_query)
        tasks = tasks_result.scalars().all()

        if not tasks:
            await message.answer("У тебя пока нет выполненных задач 📭")
            return

        for index, task in enumerate(tasks, start=1):
            deadline_text = format_deadline(task.deadline)
            await message.answer(f"{index}. ✅ {task.text}\n{deadline_text}")


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


@dp.message(Command("tasks"))
@dp.message(lambda message: message.text == "📋 Мои задачи")
async def tasks_handler(message: Message):
    telegram_id = message.from_user.id

    async with SessionLocal() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала используй /start")
            return

        tasks_query = select(Task).where(
            Task.creator_id == user.id,
            Task.status == False
        )
        tasks_result = await session.execute(tasks_query)
        tasks = tasks_result.scalars().all()

        if not tasks:
            await message.answer("У тебя пока нет задач 📭")
            return

        for index, task in enumerate(tasks, start=1):
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

            deadline_text = format_deadline(task.deadline)

            await message.answer(
                f"{index}. ❌ {task.text}\n{deadline_text}",
                reply_markup=inline_kb
            )


async def deadline_notifier():
    while True:
        try:
            async with SessionLocal() as session:
                query = select(Task).where(
                    Task.status == False,
                    Task.deadline.is_not(None)
                )
                result = await session.execute(query)
                tasks = result.scalars().all()

                now = datetime.now()

                for task in tasks:
                    delta = task.deadline - now

                    user_query = select(User).where(User.id == task.creator_id)
                    user_result = await session.execute(user_query)
                    user = user_result.scalar_one_or_none()

                    if user is None:
                        continue

                    
                    if (
                        timedelta(hours=23) <= delta <= timedelta(days=1)
                        and not task.reminded_day
                    ):
                        await bot.send_message(
                            user.telegram_id,
                            f"📅 Напоминание за 1 день!\n\n"
                            f"Задача: {task.text}\n"
                            f"{format_deadline(task.deadline)}"
                        )
                        task.reminded_day = True

                
                    if (
                        timedelta(minutes=0) <= delta <= timedelta(hours=1)
                        and not task.reminded_hour
                    ):
                        await bot.send_message(
                            user.telegram_id,
                            f"⏰ Напоминание за 1 час!\n\n"
                            f"Задача: {task.text}\n"
                            f"{format_deadline(task.deadline)}"
                        )
                        task.reminded_hour = True

                    
                    if (
                        delta.total_seconds() < 0
                        and not task.reminded_overdue
                    ):
                        await bot.send_message(
                            user.telegram_id,
                            f"⚠️ Дедлайн прошёл!\n\n"
                            f"Задача: {task.text}\n"
                            f"{format_deadline(task.deadline)}"
                        )
                        task.reminded_overdue = True

                await session.commit()

        except Exception as e:
            print(f"Ошибка в deadline_notifier: {e}")

        await asyncio.sleep(60)


async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(deadline_notifier())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())