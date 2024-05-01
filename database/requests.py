from database.models import async_session
from database.models import User, Topic, Test, Lesson, Fact
from sqlalchemy import select, update, delete, desc
import random


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user


async def get_topic(topic_number):
    async with async_session() as session:
        topic = await session.scalar(select(Topic).where(Topic.topic_number == topic_number))
    return topic


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, topic_number=1, lesson_number=1, lvl=1))
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


async def get_first_lessons(tg_id):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(lesson_number=1, topic_number=1))
        await session.commit()
        lesson = await session.scalar(select(Lesson). \
                                      where(User.tg_id == tg_id). \
                                      where(Lesson.lesson_number == User.lesson_number). \
                                      where(Lesson.topic == User.topic_number))
        if lesson:
            return lesson


async def get_test(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        lvl = user.lvl
        tests = await session.execute(select(Test).where(Test.topic == lvl))
        test_list = tests.scalars().all()  # Получаем список объектов тестов
        return test_list


async def test_done_lvl_up(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user_new_lvl = user.lvl + 1
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(lvl=user_new_lvl)
        )
        # Фиксируем изменения в базе данных
        await session.commit()


async def next_lesson(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
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
