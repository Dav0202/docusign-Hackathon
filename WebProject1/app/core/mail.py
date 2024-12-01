from pathlib import Path
from typing import List, Dict, Any

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from starlette.responses import JSONResponse
from app.core.schema import EmailSchema
from app.core import config as settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_sender_email,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_start_tls,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=settings.mail_use_credentials,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates',
)


async def simple_send(email: EmailSchema):    
    data = email.model_dump() 
    message = MessageSchema(
        subject="Altrumus SCD",
        recipients=data["email"],
        template_body=data.get('body'),
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name=data.get('file_name'))