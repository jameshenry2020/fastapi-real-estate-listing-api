from pydantic import BaseModel, Field
from typing import Optional, Union

# data serializeration and validation
class UserBase(BaseModel):
    email:str = Field(..., title="an active email address", example="testuser@gmail.com")

class UserCreate(UserBase):
    password: str = Field(..., title="a strong password", example="testpassword")


class User(UserBase):
    id: int
    is_active:bool
    is_verified: bool

    class Config:
        orm_mode = True

class AgentBase(BaseModel):
    full_name:str
    office_address:str
    phone_number:str

class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id:int
    profile_img: Union[str, None] = None
    user:User

    class Config:
        orm_mode=True



class TokenData(BaseModel):
    id:Optional[str] = None
    email:Optional[str] = None

class ForgetPasswordRequest(BaseModel):
    email:str

class ResetPassword(BaseModel):
    token:str
    password:str 
    comfirm_password:str 


class OneTimePassword(BaseModel):
    code:str

class OTPData(BaseModel):
    user_id:int
    code:Optional[str] = None

    class Config:
        orm_mode:True

