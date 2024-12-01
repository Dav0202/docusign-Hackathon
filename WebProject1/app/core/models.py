from datetime import datetime
from email.policy import default
from typing import Optional, List
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import ForeignKey, String, DateTime, Column, Integer
from fastapi_users_db_sqlalchemy.generics import GUID

import uuid

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

class OTP(Base):
    __tablename__ = 'otps'

    email = Column(String, unique=True, primary_key=True)
    otp = Column(String, nullable=False)
    jwt = Column(String, nullable=False)    
    expire_at = Column(DateTime, nullable=False)  

"""event_association_table = Table(
    "event_association_table",
    Base.metadata,
    Column("event_registration_id", ForeignKey("event_registration.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)  """

class Events(Base):
    __tablename__ = 'events'

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] =  mapped_column(
            String(length=150), unique=False, index=True, nullable=False
        )
    description : Mapped[str] =  mapped_column(
            String, unique=False, index=True, nullable=False)
    date : Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location :Mapped[str] =  mapped_column(
            String(length=450), unique=False, index=True, nullable=False
        )
    capacity :Mapped[int] =  mapped_column(
            Integer,index=True, nullable=False
            )
    attendees_count :Mapped[int] =  mapped_column(
            Integer, unique=False, index=True, nullable=False
        )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    
    events_regs: Mapped[List["Events_Registration"]]= relationship(back_populates="event")

class Events_Registration(Base):
    __tablename__ = 'event_registration'

    id: Mapped[int] = mapped_column(
        primary_key=True)
    
    event_id : Mapped[UUID_ID] = mapped_column(ForeignKey("events.id"))
    event: Mapped["Events"] = relationship(back_populates="events_regs")    
    agreement_status :Mapped[str] =  mapped_column(
            String(length=20), unique=False, index=True, nullable=False, default="pending")  
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    