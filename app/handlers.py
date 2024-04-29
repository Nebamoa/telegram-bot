from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from aiogram.enums import ParseMode

import app.keyboards as kb
import database.requests as rq

router = Router()


class Reg(StatesGroup):
    name = State()
    surname = State()
    patronymic = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply('*Добро пожаловать на курс "Морские нефтегазовые сооружения"*\n'
                        'Курс знакомит слушателей с основами правового регулирования разработки морских месторождений на шельфе\\. Приведены ключевые сведения о морской добыче нефти и газа в мире и, в частности, России\\. Подробно рассмотрены существующие формы морских нефтегазовых сооружений: стационарные и плавучие платформы, подводные добычные комплексы\\. Описаны технологические этапы по строительству площадочных морских сооружений\\.\n'
                        'Кроме того, изучены базисные принципы проектирования, строительства и эксплуатации морских трубопроводов\\. Рассмотрены условия работы подводных линейных нефтегазовых сооружений, в том числе на примере реализованных проектов магистральных газопроводов «Турецкий поток», «Северный поток»\\. Представлена классификация способов укладки морских трубопроводов, описаны структура и содержание технологических операций, преимущества и недостатки\\. Приведены методики расчета морских трубопроводов на прочность и устойчивость\\.',
                        parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.start_course)


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.reply('Меню',
                        reply_markup=kb.menu)


@router.callback_query(F.data == 'next_lesson')
async def next_lesson(callback: CallbackQuery):
    await rq.get_lessons(callback.from_user.id)
    await callback.message.answer('Э')


@router.message(Command('topics'))
async def topic(message: Message):
    await message.answer('Выберите тему')


@router.callback_query(F.data == 'cmd_start_course')
async def first_lesson(callback: CallbackQuery):
    lesson = await rq.get_lessons(callback.from_user.id)
    await callback.message.answer(f'Урок: {lesson.url}', reply_markup=kb.next)


# Тест
@router.callback_query(F.data == 'test')
async def first_lesson(callback: CallbackQuery):
    await rq.get_test(callback.from_user.id)


@router.callback_query(F.data == 'next')
async def next(callback: CallbackQuery):
    await rq.next_lesson(callback.from_user.id)
    if await rq.get_lessons(callback.from_user.id):
        lesson = await rq.get_lessons(callback.from_user.id)
        await callback.message.answer(f'Урок: {lesson.url}', reply_markup=kb.next)
    else:
        await callback.message.answer(f'Хотите ли вы пройти тест по теме?', reply_markup=kb.start_test)


@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.surname)
    await message.answer('Введите вашу фамилию')


@router.message(Reg.surname)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(Reg.name)
    await message.answer('Введите имя')


@router.message(Reg.name)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.patronymic)
    await message.answer('Введите отчество')


@router.message(Reg.patronymic)
async def reg_final(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text)
    await message.answer('Спасибо, регистрация завершена')
    data = await state.get_data()
    await rq.reg_fio(message.from_user.id, data["surname"], data["name"], data["patronymic"])
    await message.answer(
        f'Спасибо за регистрацию. \nФамилия: {data["surname"]}\nИмя: {data["name"]}\nОтчество: {data["patronymic"]}')
    await state.clear()
