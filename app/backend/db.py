from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine('postgresql+asyncpg://post_ecommerce:fastapi@localhost:5432/ecommerce_db', echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) #max_inactive_connection_lifetime=3

class Base(DeclarativeBase):
    pass