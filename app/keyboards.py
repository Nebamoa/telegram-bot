from aiogram import types

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton)
from database.requests import get_lessons
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import database.requests as rq

start_course = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать обучение', callback_data='cmd_start_course')],
])


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Программа', callback_data='get_course'), KeyboardButton(text='Пройти урок', callback_data='get_lesson')],
    [KeyboardButton(text='Пройти тест'), KeyboardButton(text='Подробнее о курсе')],
    [KeyboardButton(text='Получить сертификат')]
], resize_keyboard=True,
    input_field_placeholder='Выберите пукт меню'
)

next = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Следущий урок', callback_data='next')],
])

end_topic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Следущая тема', callback_data='next_topic')],
    [InlineKeyboardButton(text='Пройти тему заного', callback_data='re_topic')],
])

last_topic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пройти тему заного', callback_data='re_topic')],
])


start_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать тест', callback_data='test')],
])


async def all_topics():
    keyboard = ReplyKeyboardBuilder()
    topics = await rq.get_all_topic()
    for topic in topics:
        keyboard.add(KeyboardButton(text=f'{topics.index(topic)+1}. {topic.topic_name}'))
    return keyboard.adjust(2).as_markup()


async def all_lessons_topic(topic_number):
    keyboard = ReplyKeyboardBuilder()
    lesson_list = await rq.get_lessons_topic(topic_number)
    for lesson in lesson_list:
        keyboard.add(KeyboardButton(text=f'{lesson_list.index(lesson)+1}'))
    return keyboard.adjust(6).as_markup()



