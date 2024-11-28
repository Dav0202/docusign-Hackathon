from contextlib import asynccontextmanager
from importlib.metadata import requires
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth
from app.routes.users import users
from app.core.events import create_start_app_handler
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from sqlmodel import SQLModel
from app.core.database import engine

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.core.database import User, create_db_and_tables
from app.core.schema import UserCreate, UserRead, UserUpdate
from app.routes.users.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title=PROJECT_NAME, debug=DEBUG, version=VERSION)

app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True), 
    prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
