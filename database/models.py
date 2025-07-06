from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.util import win32

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(50))
    # роль пользователя, 0-никто 1-админ, 2-монтажник, 3-менеджер
    role: Mapped[int] = mapped_column(default=0)

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_order: Mapped[int] = mapped_column()


class OrderWork(Base):
    __tablename__ = 'orders_work'

    id: Mapped[int] = mapped_column(primary_key=True)
    # номер заказ-наряда
    n_order_work: Mapped[int] = mapped_column()
    # номер заказа
    n_order: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    # список работ, реализовать с помощью json.dump() в списке содержится название и количество
    list_works: Mapped[str] = mapped_column(String(1000))
    # статус ЗН, 1-новый, 2-в работе, 3-принят, 4-отменен
    status: Mapped[int] = mapped_column()
    # список фотографий приложеных к ЗН, список из id по ним можно найти путь к фотографии
    photos: Mapped[str] = mapped_column(String(1000), default=0)
    # Ответсвенный за выполнение
    responsible: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))

class Photo(Base):
    __tablename__ = 'photos'

    id: Mapped[int] = mapped_column(primary_key=True)
    # сгенерированный uuid
    id_photo: Mapped[int] = mapped_column()
    # Ссылка на фотографию
    url: Mapped[str] = mapped_column(String(200))

class ListWork(Base):
    __tablename__ = 'list_works'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)