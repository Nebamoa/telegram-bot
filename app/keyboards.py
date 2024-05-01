from aiogram import types

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton)
from database.requests import get_lessons
from aiogram.utils.keyboard import InlineKeyboardBuilder


start_course = settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать обучение', callback_data='cmd_start_course')],
])


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Программа'), KeyboardButton(text='Пройти урок')],
    [KeyboardButton(text='Пройти тест')], [KeyboardButton(text='Подробнее о курсе')]
], resize_keyboard=True,
    input_field_placeholder='Выберите пукт меню'
)

next = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Следущий урок', callback_data='next')],
])

start_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать тест', callback_data='test')],
])



