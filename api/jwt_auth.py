from fastapi.security import OAuth2PasswordBearer
from . import schema
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from datetime import datetime, timedelta
from .config import get_settings


settings=get_settings()
SECRET_KEY = f"{settings.secret}"
ALGORITHM = f"{settings.algorithm}"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth_schema=OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')

def create_access_token(data:dict):
    token_data=data.copy()
    expire= datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({'exp': expire})
    token=jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_access_token(token:str, credentials_exception):
    try:
        payload:str=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id=payload.get("user_id")
        user_email=payload.get('email')
        if user_id is None:
            raise credentials_exception
        token_data=schema.TokenData(id=user_id, email=user_email)
    except JWTError:
        raise credentials_exception
    return token_data

def decode_general_token(token:str):
    try:
        payload:str=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id=payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"the token is invalid or has expired")
        token_data=schema.TokenData(id=user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token is invalid or has expired")
    return token_data


def get_authenticate_user(token:str = Depends(oauth_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)
