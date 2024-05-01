from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton)

import random
import app.keyboards as kb
import database.requests as rq

router = Router()


class QuizStates(StatesGroup):
    WAITING_FOR_ANSWER = State()


class Reg(StatesGroup):
    name = State()
    surname = State()
    patronymic = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply('*Добро пожаловать на курс "Морские нефтегазовые сооружения"*\n'
                        'Данный курс состоит из:\n'
                        '37 видеолекций\nТесты'
                        '\n7,5 часов видео  \n3 зачетные единицы \\(108 часов\\)',
                        parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.start_course)


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.answer('Меню',
                         reply_markup=kb.main)


@router.message(F.text == 'Подробнее о курсе')
async def test(message: Message):
    await message.answer(
        '   Курс знакомит слушателей с основами правового регулирования разработки морских месторождений на шельфе\\. Приведены ключевые сведения о морской добыче нефти и газа в мире и, в частности, России\\. Подробно рассмотрены существующие формы морских нефтегазовых сооружений: стационарные и плавучие платформы, подводные добычные комплексы\\. Описаны технологические этапы по строительству площадочных морских сооружений\\.\n'
        '   Кроме того, изучены базисные принципы проектирования, строительства и эксплуатации морских трубопроводов\\. Рассмотрены условия работы подводных линейных нефтегазовых сооружений, в том числе на примере реализованных проектов магистральных газопроводов «Турецкий поток», «Северный поток»\\. Представлена классификация способов укладки морских трубопроводов, описаны структура и содержание технологических операций, преимущества и недостатки\\. Приведены методики расчета морских трубопроводов на прочность и устойчивость\\.')


@router.callback_query(F.data == 'next_lesson')
async def next_lesson(callback: CallbackQuery):
    await rq.get_lessons(callback.from_user.id)
    await callback.message.answer('Э')


@router.message(Command('topics'))
async def topic(message: Message):
    await message.answer('Выберите тему')


@router.callback_query(F.data == 'cmd_start_course')
async def first_lesson(callback: CallbackQuery):
    lesson = await rq.get_first_lessons(callback.from_user.id)
    await callback.message.answer(f'Урок: {lesson.url}', reply_markup=kb.next)


# Тест
@router.message(F.text == 'Пройти тест')
async def test(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    topic = await rq.get_topic(user.lvl)
    tests = await rq.get_test(message.from_user.id)
    random.shuffle(tests)
    await state.update_data(tests=tests)
    await message.answer(f"Тест по разделу: {topic.topic_name}")
    await ask_question(message, state, correct_answers=0, number=0, tests=tests)


async def ask_question(message: Message, state: FSMContext, correct_answers: int, number: int, tests: list):
    test_data = await state.get_data()

    if len(test_data['tests']) == number:
        # Подсчет процента правильных ответов
        percentage_correct = round((correct_answers / len(test_data['tests'])) * 100, 1)
        if percentage_correct >= 60:
            await message.answer(
                f"Поздравляем! Вы прошли тест с результатом {percentage_correct}% правильных ответов. Вам доступен следущий раздел")
            await state.clear()
            await rq.test_done_lvl_up(message.from_user.id)
        else:
            await message.answer(
                f"Простите, вы не набрали необходимый балл. Ваш результат: {percentage_correct}% правильных ответов."
                f"\nПовторите данный раздел и попробуйте пройти тест снова")
            await state.clear()
        return
    question = tests[0]
    await message.answer(f'Вопрос [{number + 1}/{len(test_data["tests"])}] {question.question}\n'
                         f'1. {(test_data["tests"][number]).answer_first}\n'
                         f'2. {(test_data["tests"][number]).answer_second}\n'
                         f'3. {(test_data["tests"][number]).answer_third}\n'
                         f'4. {(test_data["tests"][number]).answer_fourth}')

    # # Формируем клавиатуру для выбора ответа
    test_answers = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='1'), KeyboardButton(text='2')],
        [KeyboardButton(text='3'), KeyboardButton(text='4')],
    ], resize_keyboard=True
    )
    await message.answer(f"Выберите правильный ответ: {(test_data['tests'][number]).answer}", reply_markup=test_answers)
    # Устанавливаем состояние, ожидая ответ пользователя
    await state.update_data(number=number)
    await state.set_state(QuizStates.WAITING_FOR_ANSWER)


# Обработчик ответов пользователя
@router.message(QuizStates.WAITING_FOR_ANSWER)
async def process_answer(message: Message, state: FSMContext):
    user_answer = message.text[0]
    # Получаем текущий вопрос
    current_question = await state.get_data()
    number = current_question['number']
    correct_answer = str((current_question['tests'])[number].answer)
    if user_answer == correct_answer:
        await message.answer("Правильно!.")
        await state.update_data(correct_answers=current_question.get('correct_answers', 0) + 1)
    else:
        await message.answer(f"Неправильно! Правильный ответ: {correct_answer}.")
    tests = current_question['tests']
    number = current_question['number'] + 1
    # Задаем следующий вопрос
    await ask_question(message, state, correct_answers=current_question.get('correct_answers', 0),
                       number=number, tests=tests)


@router.callback_query(F.data == 'next')
async def next(callback: CallbackQuery):
    result = await (rq.next_lesson(callback.from_user.id))
    if result is not None:
        lesson = await rq.get_lessons(callback.from_user.id)
        await callback.message.answer(f'Урок: {lesson.url}', reply_markup=kb.next)
    else:
        user = await rq.get_user(callback.from_user.id)
        topic = await rq.get_topic(user.topic_number)
        await callback.message.answer(f'Поздравляю. Вы прошли тему "{topic.topic_name}".\n'
                                      f'Теперь Вы можете пройти тест по данной теме', reply_markup=kb.main)


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
