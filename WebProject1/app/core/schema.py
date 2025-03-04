from datetime import datetime
from typing import List, Optional, Type
from pydantic import BaseModel, EmailStr
import uuid
from fastapi_users import schemas
from app.core.database import Base, Events as Event, Events_Registration as EVr

class BaseInDB(BaseModel):
    # base schema for every schema that stored in DB.
    # provides a default method for converting
    # Pydantic objects to SQLAlchemy objects
    class Config:
        orm_model: Optional[Type[Base]] = None

    def to_orm(self) -> Base:
        if not self.Config.orm_model:
            raise AttributeError('Class has not defined Config.orm_model')
        return self.Config.orm_model(**dict(self))  # pylint: disable=not-callable

class BaseUpdateInDB(BaseInDB):
    id: int

class ValidationSchema(BaseModel):
    email: EmailStr
    link: str

class ValidationSchemaQr(BaseModel):
    qr_code: str   
    event_name: str    


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: ValidationSchemaQr
    file_name: str

class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    last_name: str

class Otp(BaseModel):
    email: str   
    otp: str
    expire_at: datetime
            

class UserRegisterResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str   

class UserLoginResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str      

class EventsRead(BaseModel):
    id: uuid.UUID    
    name: str
    description : str
    date : datetime
    location : str 
    capacity : int 
    #events_regs: list   
    created_at: datetime
    created_by_id: uuid.UUID   
    attendees_count: int     

class Events(BaseModel):
    name: str
    description : str
    date : datetime
    location : str 
    capacity : int 
    #events_regs: list   

class EventInDB(BaseInDB, Events):
    created_by_id: uuid.UUID
    
    class Config(BaseInDB.Config):
        orm_model = Event    

class UpdateEventInDB(BaseInDB, Events):
    id: uuid.UUID  
    created_by_id: uuid.UUID    

    class Config(BaseInDB.Config):
        orm_model = Event


class DonorBase(BaseModel):
    pass

class VolunteerBase(BaseModel):
    pass  


class Event_Registration_Read(BaseModel):
    id: int
    user_id : uuid.UUID
    event_id : uuid.UUID
    agreement_status : str
    created_at: datetime

class Event_Registration(BaseModel):
    user_id : uuid.UUID
    event_id : uuid.UUID
    #agreement_status : str

class Event_RegistrationInDB(BaseInDB, Event_Registration):
    class Config(BaseInDB.Config):
        orm_model = EVr

class Update_Event_RegistrationInDB(BaseInDB, Event_Registration):
    id: uuid.UUID  
    created_by_id: uuid.UUID    

    class Config(BaseInDB.Config):
        orm_model = Event