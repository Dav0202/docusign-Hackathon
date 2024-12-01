from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.events import create_start_app_handler
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from app.core.database import create_db_and_tables, User
from app.core.schema import UserCreate, UserRead, UserUpdate
from app.routes.users.users import auth_backend, fastapi_users
from app.routes.events.events import router as event_router

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
app.include_router(router=event_router, prefix="/app")
