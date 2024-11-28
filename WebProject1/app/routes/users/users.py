import uuid
from typing import Optional, Union
from fastapi.responses import JSONResponse
from loguru import logger
from fastapi import Depends, Request, status
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin, models
from app.core.database import User, get_user_db
from app.core.schema import UserCreate
from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash, exceptions
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.routes.users.fastapi_users import MyFastAPIUsers
from fastapi_users.router.common import ErrorCode, ErrorModel
import jwt
from fastapi_users import exceptions, models
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.password import PasswordHelper
from app.core.config import SECRET_KEY, CHANGE_PASSWORD_URL
from app.core.utils import OTPManager
import fastapi_users

SECRET = str(SECRET_KEY)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.email} has registered.")
        await self.request_verify(user, request)        

    async def request_verify(
        self, user: models.UP, request: Optional[Request] = None,
    ) -> None:

        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )        
        
        otp_manager =  OTPManager()
        generated_otp = await otp_manager.generate_otp(user, token)
        
        await self.on_after_request_verify(user, generated_otp, request)        

    async def verify(self, generated_otp: str, request: Optional[Request] = None) -> models.UP:
        otp_manager =  OTPManager()           
        validated_otp = await otp_manager.validate_otp(generated_otp)
        if not validated_otp or validated_otp['is_verified'] == False:          
            raise exceptions.InvalidVerifyToken()             
        try:
            data = decode_jwt(
                validated_otp['otp_data'],
                self.verification_token_secret,
                [self.verification_token_audience],
            )         
        except jwt.PyJWTError:
            raise exceptions.InvalidVerifyToken()        
        
        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise exceptions.InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except exceptions.UserNotExists:
            raise exceptions.InvalidVerifyToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidVerifyToken()

        if parsed_id != user.id:
            raise exceptions.InvalidVerifyToken()

        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})
        await otp_manager.del_otp(generated_otp)
        await self.on_after_verify(verified_user, request)

        return verified_user        

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):        
        reset_link = CHANGE_PASSWORD_URL.format(token=token)
        
        print(f"User {user.id} has forgot their password. Reset link token: {reset_link}")
        return JSONResponse(content={"detail": "reset link sent"})

    async def on_after_request_verify(
        self, user: User, generated_otp: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {generated_otp}")

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        logger.info(f"User {user.email} Verified.")

    async def on_after_reset_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
         logger.info(f"User {user.email} password reset sucesssful.")
        
    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )        


password_hash = PasswordHash((
    Argon2Hasher(),
))
password_helper = PasswordHelper(password_hash)
        
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, password_helper)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = MyFastAPIUsers(get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)   