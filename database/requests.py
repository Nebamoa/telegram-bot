from database.models import async_session
from database.models import User, Topic, Test, Lesson, Fact
from sqlalchemy import select, update, delete, desc
import random
import datetime


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user


async def get_topic(topic_number):
    #Получаем тему по его номеру
    async with async_session() as session:
        topic = await session.scalar(select(Topic).where(Topic.topic_number == topic_number))
    return topic


async def set_user(tg_id):
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            session.add(User(tg_id=tg_id, topic_number=1, lesson_number=1, lvl='00000'))
            await session.commit()


async def reg_fio(tg_id, surname, name, patronymic):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            await session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(surname=surname, first_name=name, patronymic=patronymic))
            await session.commit()


async def get_lessons(tg_id):
    async with async_session() as session:
        lesson = await session.scalar(select(Lesson). \
                                      where(User.tg_id == tg_id). \
                                      where(Lesson.lesson_number == User.lesson_number). \
                                      where(Lesson.topic == User.topic_number))
        if lesson:
            return lesson



async def get_lessons_topic(topic_number):
    async with async_session() as session:
        lessons = await session.execute(select(Lesson).where(Lesson.topic == topic_number))
        lessons_list = lessons.scalars().all()
        if lessons_list:
            return lessons_list



async def get_first_lessons(tg_id, topic_number):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(lesson_number=1, topic_number=topic_number))
        await session.commit()
        lesson = await get_lessons(tg_id)
        if lesson:
            return lesson


async def get_test(number):
    async with async_session() as session:
        tests = await session.execute(select(Test).where(Test.topic == number))
        test_list = tests.scalars().all()  # Получаем список объектов тестов
        return test_list


async def test_done_lvl_up(tg_id, test_number):
    async with async_session() as session:
        user = await get_user(tg_id)
        test_number = int(test_number)
        lvl = user.lvl
        lvl_ = lvl[0:test_number-1] + '1' + lvl[test_number:]
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(lvl=lvl_)
        )
        # Фиксируем изменения в базе данных
        await session.commit()


async def next_lesson(tg_id):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            # Увеличиваем lesson_number на 1
            new_lesson_number = user.lesson_number + 1
            lesson = await session.scalar(select(Lesson). \
                                          where(Lesson.lesson_number == new_lesson_number). \
                                          where(Lesson.topic == user.topic_number))
            if lesson:
                # Выполняем обновление lesson_number для пользователя
                await session.execute(
                    update(User)
                    .where(User.tg_id == tg_id)
                    .values(lesson_number=new_lesson_number)
                )
                # Фиксируем изменения в базе данных
                await session.commit()
                return 1
            else:
                return None


async def get_all_topic():
    async with async_session() as session:
        topic = await session.execute(select(Topic))
        topic_list = topic.scalars().all()  # Получаем список объектов
        return topic_list



async def set_topic_lesson_user(tg_id, topic_number, lesson_number):
    async with async_session() as session:
        user = await get_user(tg_id)
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(topic_number=topic_number, lesson_number=lesson_number)
        )
        # Фиксируем изменения в базе данных
        await session.commit()


async def time_last_test(tg_id):
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(date=current_date))
        await session.commit()


# Функция для обновления времени последнего использования
async def update_last_usage(tg_id):
    async with async_session() as session:
        now = datetime.datetime.now().strftime('%d.%m.%Y')
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(last_use_course=now))
        await session.commit()


async def get_last_usage(tg_id):
    async with async_session() as session:
        user = await get_user(tg_id)
        return user.last_use_course
        await session.commit()

async def get_all_users():
    async with async_session() as session:
        users = await session.execute(select(User))
        users_list = users.scalars().all()  # Получаем список объектов
        return users_list


async def get_random_fact():
    async with async_session() as session:
        facts = await session.execute(select(Fact))
        facts_list = facts.scalars().all()  # Получаем список объектов
        return facts_list