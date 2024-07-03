from database.models import async_session
from database.models import User, Topic, Test, Lesson, Fact, Result
from sqlalchemy import select, update, delete, desc
import random
import datetime
async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user
async def get_result(id_user):
    async with async_session() as session:
        result = await session.scalar(select(Result).where(Result.id_user == id_user))
    return result
async def get_topic(topic_number):
    async with async_session() as session:
        topic = await session.scalar(select(Topic).where(Topic.topic_number == topic_number))
    return topic
async def set_user(tg_id):
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            session.add(User(tg_id=tg_id, topic_number=1, lesson_number=1))
            await session.commit()
            user = await get_user(tg_id)
            session.add(Result(id_user=user.id))
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
async def get_final_test():
    async with async_session() as session:
        tests = await session.execute(select(Test))
        test_list = tests.scalars().all()
        return test_list
async def test_done_lvl_up(tg_id, test_number):
    async with async_session() as session:
        user = await get_user(tg_id)
        test_number = int(test_number) - 1
        tests = [user.Test1, user.Test2, user.Test3, user.Test4, user.Test5]
        tests[test_number] = 1
        await session.execute(update(User)
            .where(User.tg_id == tg_id)
            .values(Test1=tests[0], Test2=tests[1], Test3=tests[2], Test4=tests[3], Test5=tests[4]))
        await session.commit()
async def test_done(id_user, test_number, result):
    async with async_session() as session:
        result_ = await get_result(id_user)
        test_number = int(test_number) - 1
        results = [result_.Test1, result_.Test2, result_.Test3, result_.Test4, result_.Test5]
        attempts = [result_.attempts1, result_.attempts2, result_.attempts3, result_.attempts4, result_.attempts5]
        if results[test_number] < result:
            results[test_number] = result
        attempts[test_number] += 1
        await session.execute(
            update(Result)
            .where(Result.id_user == id_user)
            .values(Test1=results[0], Test2=results[1], Test3=results[2], Test4=results[3], Test5=results[4],
                    attempts1=attempts[0], attempts2=attempts[1], attempts3=attempts[2], attempts4=attempts[3],
                    attempts5=attempts[4]))
        await session.commit()
async def final_test_done(id_user, result):
    async with async_session() as session:
        result_ = await get_result(id_user)
        results = result_.Final_test
        attempts = result_.attempts_final
        if results < result:
            results = result
        attempts += 1
        await session.execute(
            update(Result)
            .where(Result.id_user == id_user)
            .values(Final_test=results, attempts_final=attempts)
        )
        await session.commit()
async def next_lesson(tg_id):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            new_lesson_number = user.lesson_number + 1
            lesson = await session.scalar(select(Lesson). \
                                          where(Lesson.lesson_number == new_lesson_number). \
                                          where(Lesson.topic == user.topic_number))
            if lesson:
                await session.execute(
                    update(User)
                    .where(User.tg_id == tg_id)
                    .values(lesson_number=new_lesson_number))
                await session.commit()
                return 1
            else:
                return None
async def get_all_topic():
    async with async_session() as session:
        topic = await session.execute(select(Topic))
        topic_list = topic.scalars().all()
        return topic_list
async def set_topic_lesson_user(tg_id, topic_number, lesson_number):
    async with async_session() as session:
        user = await get_user(tg_id)
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(topic_number=topic_number, lesson_number=lesson_number)
        )
        await session.commit()
async def time_last_test(tg_id):
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(date=current_date))
        await session.commit()
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
#diplom
async def set_lesson(topic, text, url):
    async with async_session() as session:
        lesson = await get_lessons_topic(topic)
        lessons = await session.execute(select(Lesson))
        lessons = lessons.scalars().all()
        len = len(lesson)
        session.add(Lesson(id=len(lessons)+1, lesson_number = len+1, url=url, lesson_text=text, topic=topic))
        await session.commit()