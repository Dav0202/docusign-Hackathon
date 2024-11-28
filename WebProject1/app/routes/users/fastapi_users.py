from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from app.core.database import User
import uuid
from app.routes.users.reset import get_reset_password_router


class MyFastAPIUsers(FastAPIUsers[User, uuid.UUID]):    
    
    def get_reset_password_router(self) -> APIRouter:
        """Return a reset password process router."""
        return get_reset_password_router(self.get_user_manager)
