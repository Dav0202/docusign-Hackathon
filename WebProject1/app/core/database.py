from collections.abc import AsyncGenerator
from time import timezone
from typing import Annotated, Union
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import ForeignKey, String, DateTime, Column, Integer, Table, UniqueConstraint
from datetime import datetime
from typing import Optional, List, Any
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, DateTime, Column, UUID
import uuid
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy import inspect


POSTGRES_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_async_engine(POSTGRES_DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)  


UUID_ID = uuid.UUID

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
    events_attending: Mapped[List["Events_Registration"]]= relationship(back_populates="user")    

    my_events: Mapped[List["Events"]]= relationship(back_populates="created_by")    

class OTP(Base):
    __tablename__ = 'otps'

    email = Column(String, unique=True, primary_key=True)
    otp = Column(String, nullable=False)
    jwt = Column(String, nullable=False)    
    expire_at = Column(DateTime, nullable=False)  

class Events(Base):
    __tablename__ = 'events'

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    created_by_id : Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(back_populates="my_events")       
    name: Mapped[str] =  mapped_column(
            String(length=150), unique=False, index=True, nullable=False
        )
    description : Mapped[str] =  mapped_column(
            String, unique=False, index=True, nullable=False)
    date : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location :Mapped[str] =  mapped_column(
            String(length=450), unique=False, index=True, nullable=False
        )
    capacity :Mapped[int] =  mapped_column(
            Integer,index=True, nullable=False
            )
    attendees_count :Mapped[int] =  mapped_column(
            Integer, unique=False, index=True, nullable=False, default=0
        )
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now())
    
    events_regs: Mapped[List["Events_Registration"]]= relationship(back_populates="event")   
 

class Events_Registration(Base):
    __tablename__ = 'event_registration'

    id: Mapped[int] = mapped_column(
        primary_key=True)
    
    user_id : Mapped[UUID_ID] = mapped_column(ForeignKey("user.id",ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="events_attending") 
    event_id : Mapped[UUID_ID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    event: Mapped["Events"] = relationship(back_populates="events_regs")    
    agreement_status :Mapped[str] =  mapped_column(
            String(length=20), unique=False, index=True, nullable=False, default="pending")  
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "event_id", name="unique_user_event"),)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
