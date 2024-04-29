import random
import asyncio
from datetime import datetime, timedelta
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher, types
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import app.keyboards as kb

router = Router()


# Импорт конфигурации и данных
from config import BOT_TOKEN
from data.topics import TOPICS
from data.facts import FACTS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def remind_user(chat_id, days):
    try:
        # Вычисляем дату через 'days' дней от текущего момента
        remind_date = datetime.now() + timedelta(days=days)

        # Ожидаем до нужной даты
        await asyncio.sleep(days * 24 * 60 * 60)

        # Выбираем случайный факт для напоминания (здесь пример)
        facts = [
            "Интересный факт 1",
            "Интересный факт 2",
            "Интересный факт 3"
        ]
        random_fact = random.choice(facts)

        # Отправляем напоминание пользователю
        await bot.send_message(chat_id, f"Прошло {days} дней! Вот интересный факт для вас:\n{random_fact}")
    except Exception as e:
        print(f"Ошибка при отправке напоминания: {e}")

# Команда /start
@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот микрообучения. Выбери тему для изучения или пройди тест по темам, "
                         "написав /test.")


# Обработчик выбора темы
@router.message(F.text == (lambda message: message.text in TOPICS.keys())
async def select_topic(message: types.Message):
    topic = message.text
    await message.answer(f"Ты выбрал тему: {topic}. Начнем изучение!")

    # Отправка видеоуроков по теме
    for video in TOPICS[topic]['videos']:
        await message.answer(f"Видеоурок: {video['title']}\nОписание: {video['description']}\n{video['url']}")

    # Напоминалка через 3 дня
    await remind_user(message.chat.id, 3)


# Напоминалка через определенное количество
