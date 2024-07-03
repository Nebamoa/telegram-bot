from sqlalchemy import BigInteger, Integer, String, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)
class Base(AsyncAttrs, DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String(40))
    surname: Mapped[str] = mapped_column(String(40))
    patronymic: Mapped[str] = mapped_column(String(40))
    lesson_number: Mapped[int] = mapped_column()
    topic_number: Mapped[int] = mapped_column()
    Test1: Mapped[int] = mapped_column(default=0)
    Test2: Mapped[int] = mapped_column(default=0)
    Test3: Mapped[int] = mapped_column(default=0)
    Test4: Mapped[int] = mapped_column(default=0)
    Test5: Mapped[int] = mapped_column(default=0)
    date: Mapped[str] = mapped_column()
    last_use_course: Mapped[str] = mapped_column()
    Final_test: Mapped[int] = mapped_column(default=0)
class Result(Base):
    __tablename__ = 'Results'
    id: Mapped[int] = mapped_column(primary_key=True)
    id_user = mapped_column(Integer)
    Test1: Mapped[float] = mapped_column(default=0)
    Test2: Mapped[float] = mapped_column(default=0)
    Test3: Mapped[float] = mapped_column(default=0)
    Test4: Mapped[float] = mapped_column(default=0)
    Test5: Mapped[float] = mapped_column(default=0)
    attempts1: Mapped[int] = mapped_column(default=0)
    attempts2: Mapped[int] = mapped_column(default=0)
    attempts3: Mapped[int] = mapped_column(default=0)
    attempts4: Mapped[int] = mapped_column(default=0)
    attempts5: Mapped[int] = mapped_column(default=0)
    Final_test: Mapped[float] = mapped_column(default=0)
    attempts_final: Mapped[int] = mapped_column(default=0)
class Topic(Base):
    __tablename__ = 'topics'
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_name: Mapped[str] = mapped_column()
    topic_number: Mapped[int] = mapped_column()
class Test(Base):
    __tablename__ = 'tests'
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column()
    answer_first: Mapped[str] = mapped_column()
    answer_second: Mapped[str] = mapped_column()
    answer_third: Mapped[str] = mapped_column()
    answer_fourth: Mapped[str] = mapped_column()
    answer: Mapped[int] = mapped_column()
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'))
class Lesson(Base):
    __tablename__ = 'lessons'
    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_text: Mapped[str] = mapped_column()
    lesson_number: Mapped[int] = mapped_column()
    url: Mapped[str] = mapped_column()
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'))
class Fact(Base):
    __tablename__ = 'Facts'
    id: Mapped[int] = mapped_column(primary_key=True)
    fact_text: Mapped[str] = mapped_column()
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
