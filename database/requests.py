from database.models import async_session
from database.models import User, Order, OrderWork, ListWork, Photo
from sqlalchemy import select, update, delete

async def set_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()

async def get_order(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        print(user)
        return await session.scalars(select(OrderWork).where(OrderWork.responsible == user.id))