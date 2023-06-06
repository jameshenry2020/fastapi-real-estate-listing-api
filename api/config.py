import pathlib
import os
from pydantic import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_username : str
    db_password: str
    db_name: str
    secret:str
    algorithm:str
    mail_username:str
    mail_password:str
    mail_from:str
    mail_server:str
    cloud_name:str
    cloud_api_key:str
    cloud_api_secret:str

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"



def get_settings():
    return Settings()

get_settings()

