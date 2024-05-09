from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from aiogram.enums import ParseMode
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton, InputFile, FSInputFile, BufferedInputFile, ReplyKeyboardRemove)
from aiogram import Bot
import os
import asyncio
import random
from datetime import datetime
import app.keyboards as kb
import database.requests as rq
from data.certificate import generate_certificate

router = Router()

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def get_topics():
    topics = await rq.get_all_topic()
    topic_list = []
    for topic in topics:
        topic_list.append(f'{topics.index(topic) + 1}. {topic.topic_name}')
    return topic_list


async def check_and_notify():
    while True:
        list_remind_send = ['Привет! Напоминаем, что доступен новый урок на курсе. Погрузимся в '
                            'увлекательный мир морских нефтегазовых сооружений вместе!',
                            'Приветствуем! Убедитесь, что вы не пропустили последний урок на курсе. '
                            'Он действительно увлекательный!',
                            'Здравствуйте! Новый урок о морских нефтегазовых сооружениях уже ждет вас на курсе. '
                            'Приглашаем присоединиться и узнать больше!']
        now = datetime.now()
        now_ = now.strftime('%d.%m.%Y')
        users = await rq.get_all_users()
        for user in users:
            date1 = datetime(int(now_[6:10]), int(now_[3:5]), int(now_[0:2]))  # Дата 1
            date2 = datetime(int(user.last_use_course[6:10]), int(user.last_use_course[3:5]),
                             int(user.last_use_course[0:2]))  # Дата 1
            if now.hour == 19:
                print('now.hour')
                difference = date1 - date2
                print(difference.days)
                if ((difference.days == 3 or difference.days == 6) and (user.topic_number and user.lesson_number == 1) and
                        (user.lvl == '00000')):
                    await bot.send_message(chat_id=user.tg_id, text='Привет! Мы заметили, что ты ещё не начал проходить'
                                                                    ' наш курс. Можем ли мы чем-нибудь помочь?')
                elif 3 <= difference.days <= 5:
                    facts_list = await rq.get_random_fact()
                    await bot.send_message(chat_id=user.tg_id, text=f'{(random.choice(facts_list)).fact_text}')
                elif difference.days == 6:
                    await bot.send_message(chat_id=user.tg_id, text=f'{random.choice(list_remind_send)}')
                elif difference.days == 10:
                    await bot.send_message(chat_id=user.tg_id, text=f'{random.choice(list_remind_send)}')

        print('итерация')
        # Засыпаем на минуту
        await asyncio.sleep(3600)


topics_names_list = asyncio.run(get_topics())


class LessonChoice(StatesGroup):
    Choice = State()
    Choice_ = State()


class QuizStates(StatesGroup):
    WAITING_FOR_ANSWER = State()
    choice_test = State()


class Reg(StatesGroup):
    name = State()
    surname = State()
    patronymic = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply('*Добро пожаловать на курс "Морские нефтегазовые сооружения"*\n'
                        'Данный курс состоит из:\n'
                        '37 видеолекций\nТестов'
                        '\n7,5 часов видео  \n3 зачетных единиц \\(108 часов\\)',
                        parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.start_course)
    await rq.update_last_usage(message.from_user.id)


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.answer('Меню',
                         reply_markup=kb.main)


@router.message(F.text == 'Подробнее о курсе')
async def about(message: Message):
    await message.answer(
        '   Курс знакомит слушателей с основами правового регулирования разработки морских месторождений на шельфе\\. Приведены ключевые сведения о морской добыче нефти и газа в мире и, в частности, России\\. Подробно рассмотрены существующие формы морских нефтегазовых сооружений: стационарные и плавучие платформы, подводные добычные комплексы\\. Описаны технологические этапы по строительству площадочных морских сооружений\\.\n'
        '   Кроме того, изучены базисные принципы проектирования, строительства и эксплуатации морских трубопроводов\\. Рассмотрены условия работы подводных линейных нефтегазовых сооружений, в том числе на примере реализованных проектов магистральных газопроводов «Турецкий поток», «Северный поток»\\. Представлена классификация способов укладки морских трубопроводов, описаны структура и содержание технологических операций, преимущества и недостатки\\. Приведены методики расчета морских трубопроводов на прочность и устойчивость\\.',
        parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command('topics'))
async def topic(message: Message):
    await message.answer('Выберите тему')


@router.callback_query(F.data == 'cmd_start_course')
async def first_lesson(callback: CallbackQuery):
    lesson = await rq.get_first_lessons(callback.from_user.id, 1)
    await callback.message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}',
                                  reply_markup=kb.next)


@router.callback_query(F.data == 're_topic')
async def first_lesson_topic(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)
    lesson = await rq.get_first_lessons(callback.from_user.id, user.topic_number)
    await callback.message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}',
                                  reply_markup=kb.next)


@router.message(F.text == 'Пройти урок')
async def get_lesson(message: Message):
    lesson = rq.get_lessons(message.from_user.id)
    if lesson:
        lesson = await rq.get_lessons(message.from_user.id)
        await message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}',
                             reply_markup=kb.next)
    else:
        await message.answer('NONE')
    await rq.update_last_usage(message.from_user.id)


# Тест
@router.message(F.text == 'Пройти тест')
async def test(message: Message, state: FSMContext):
    user = await rq.get_user(message.from_user.id)
    topics = await rq.get_all_topic()
    topic_ = ''
    for topic in topics:
        if user.lvl[topics.index(topic)] == '1':
            topic_ += (f'{topics.index(topic) + 1}. {topic.topic_name} - Пройден✅\n')
        else:
            topic_ += (f'{topics.index(topic) + 1}. {topic.topic_name} - Не пройден❌ \n')
    await message.answer(f"По какому разделу вы хотите пройти тест?\n{topic_}", reply_markup=await kb.all_topics())
    await state.set_state(QuizStates.choice_test)


@router.message(QuizStates.choice_test)
async def process_answer(message: Message, state: FSMContext):
    test_number = message.text[0]
    if message.text == 'Программа':
        await get_all_topics(message, state)
    elif message.text == 'Получить сертификат':
        await generate(message)
        return 0
    tests = await rq.get_test(test_number)
    random.shuffle(tests)
    await state.update_data(tests=tests, test_number=test_number)
    await ask_question(message, state, correct_answers=0, number=0, tests=tests)


async def ask_question(message: Message, state: FSMContext, correct_answers: int, number: int, tests: list):
    test_data = await state.get_data()
    if len(test_data['tests']) == number:
        # Подсчет процента правильных ответов
        percentage_correct = round(((correct_answers + 1) / len(test_data['tests'])) * 100, 1)
        if percentage_correct >= 60:
            await rq.test_done_lvl_up(message.from_user.id, test_data['test_number'])
            user = await rq.get_user(message.from_user.id)
            if user.lvl != '11111':
                await message.answer(
                    f"Поздравляем! Вы прошли тест с результатом {percentage_correct}% правильных ответов."
                )
            else:
                await rq.time_last_test(message.from_user.id)
                await message.answer(
                    f"Поздравляем! Вы прошли тест с результатом {percentage_correct}% правильных ответов.\n"
                    f"На данный момент вы прошли все тесты. Теперь вы можете получить сертификат из пункта меню"
                )
            await rq.update_last_usage(message.from_user.id)
            await state.clear()

        else:
            await message.answer(
                f"Простите, вы не набрали необходимый балл. Ваш результат: {percentage_correct}% правильных ответов."
                f"\nПовторите данный раздел и попробуйте пройти тест снова")
            await rq.update_last_usage(message.from_user.id)
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
    user = await  rq.get_user(callback.from_user.id)
    if result is not None:
        lesson = await rq.get_lessons(callback.from_user.id)
        await callback.message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}',
                                      reply_markup=kb.next)
    elif user.topic_number == len(await rq.get_all_topic()):
        await callback.message.answer(f'Вы прошли последний раздел данного курса. Пройдите тесты и '
                                      f'получите сертификат.', reply_markup=kb.last_topic)
    else:
        await callback.message.answer(f'Вы прошли данный раздел. Не забудьте пройти тест по данной теме\n '
                                      f'Перейти в следущий раздел?', reply_markup=kb.end_topic)
    await rq.update_last_usage(callback.from_user.id)


@router.callback_query(F.data == 'next_topic')
async def next_topic(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)
    lesson = await rq.get_first_lessons(callback.from_user.id, user.topic_number + 1)
    await callback.message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}',
                                  reply_markup=kb.next)
    await rq.update_last_usage(callback.from_user.id)


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


async def topic_list_take(topic_list):
    text = ''
    for topic in topic_list:
        text += f'{topic_list.index(topic) + 1}. {topic.topic_name}\n'
    return f'{text}'


@router.message(F.text == 'Программа')
async def get_all_topics(message: Message, state: FSMContext):
    topic_list = await rq.get_all_topic()

    await message.reply(f'Список тем:\n'
                        f'{await topic_list_take(topic_list)}'
                        f'\nВыберите нужную тему в меню если хотите перейти к ней',
                        reply_markup=await kb.all_topics())
    await state.set_state(LessonChoice.Choice)


@router.message(LessonChoice.Choice)
async def choice(message: Message, state: FSMContext):
    topic_number = message.text[0]
    ls = await rq.get_lessons_topic(topic_number)
    topic_ = await rq.get_topic(topic_number)
    list_ = await lessons_list(lessons=ls)
    await message.reply(f'Список уроков:\n'
                        f'{list_}',
                        reply_markup=await kb.all_lessons_topic(topic_number))
    await state.update_data(topic=topic_number, topic_name=topic_.topic_name)
    await state.set_state(LessonChoice.Choice_)


@router.message(LessonChoice.Choice_)
async def choice_(message: Message, state: FSMContext):
    lesson_number = message.text[0]
    data = await state.get_data()
    await rq.set_topic_lesson_user(message.from_user.id, topic_number=data['topic'], lesson_number=lesson_number)
    await message.answer(f'Вы выбрали урок номер {lesson_number} раздела "{data["topic_name"]}"',
                         reply_markup=ReplyKeyboardRemove())
    await get_lesson(message)
    await state.clear()


async def lessons_list(lessons):
    list_ = ''
    for lesson in lessons:
        list_ += f'{lessons.index(lesson) + 1}. {lesson.lesson_text}\n'
    return list_


@router.message(F.text.in_(topics_names_list))
async def get_all_topic(message: Message):
    topics = await rq.get_all_topic()
    topics_ = []
    for topic in topics:
        topics_.append(topic.topic_name)
    index = topics_.index(message.text[3:])
    lesson = await rq.get_first_lessons(message.from_user.id, topics[index].topic_number)
    await message.answer(f'Урок {lesson.lesson_number}. {lesson.lesson_text}: {lesson.url}', reply_markup=kb.next)


@router.message(F.text == 'Получить сертификат')
async def generate(message: Message):
    user = await rq.get_user(message.from_user.id)
    if (user.first_name or user.patronymic or user.surname) is None:
        await message.answer(f'Вы не зарегистрировали своё ФИО в системе. Нажмите команду /reg чтобы ввести своё ФИО')
    if user.lvl == '11111':
        await generate_certificate(f' {user.surname} {user.first_name} {user.patronymic}',
                                   f'{user.date}', f'{user.id}', f'data/certificate_{user.id}.pdf')
        await message.answer_document(document=FSInputFile(f'data/certificate_{user.id}.pdf'))
        os.remove(f'data/certificate_{user.id}.pdf')
    else:
        await message.answer(f'Недоступно, пока не пройдены все тесты.')
