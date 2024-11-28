from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, DateTime, Column

POSTGRES_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_async_engine(POSTGRES_DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    __table_args__ = {'extend_existing': True}    
    first_name: Mapped[str] = mapped_column(
            String(length=320), unique=False, index=True, nullable=False
        )
    last_name: Mapped[str] = mapped_column(
            String(length=320), unique=False, index=True, nullable=False
        )
    phone : Mapped[str] = mapped_column(
            String(length=12), unique=True, index=True, nullable=False
        )
    role: Mapped[str] = mapped_column(
            String(length=50), unique=False, index=True, nullable=False
        )

class OTP(Base):
    __tablename__ = 'otps'

    email = Column(String, unique=True, primary_key=True)
    otp = Column(String, nullable=False)
    jwt = Column(String, nullable=False)    
    expire_at = Column(DateTime, nullable=False)    

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
