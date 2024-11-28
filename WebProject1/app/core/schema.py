from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid
from fastapi_users import schemas


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

class DonorBase(BaseModel):
    pass

class VolunteerBase(BaseModel):
    pass  