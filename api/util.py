import pyotp
from typing import List
from fastapi import BackgroundTasks
from passlib.context import CryptContext
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from .config import get_settings
pwd_context=CryptContext(schemes=['bcrypt'])

settings=get_settings()
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(raw_password:str, hashed_password:str):
    return pwd_context.verify(raw_password, hashed_password)

conf = ConnectionConfig(
    MAIL_USERNAME =f"{settings.mail_username}",
    MAIL_PASSWORD = f"{settings.mail_password}",
    MAIL_FROM = f"{settings.mail_from}",
    MAIL_PORT = 2525,
    MAIL_SERVER = f"{settings.mail_server}",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

def send_email(background_tasks: BackgroundTasks, subject:str, recipient:List, message:str):
    message=MessageSchema(
        subject=subject,
        recipients=recipient,
        body=message,
        subtype="html"
    )
    fm = FastMail(conf)
    background_tasks.add_task(
       fm.send_message, message)


secret = pyotp.random_base32()
totp = pyotp.TOTP(secret, interval=120)
def generate_otp(): 
    otp=totp.now()
    return otp

def verify_otp(code):
    return totp.verify(code)