import json
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Union, List, Type, TypeVar
from fastapi import Form, HTTPException, status
from fastapi.encoders import jsonable_encoder

Serialized = TypeVar("Serialized", bound=BaseModel)




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

class PropertyBase(BaseModel):
    title:str 
    description:str
    price: float 
    country:str 
    city:str 
    street_address:str 
    property_type: str 
    advert_type: str 
    num_of_rooms: int 

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        orm_mode=True

class PropertyImageBase(BaseModel):
    img_url:str


class PropertyImageCreate(PropertyImageBase):
    property_id:int
    


class PropertyImageOut(PropertyImageBase):
    id:int

    class Config:
        orm_mode=True

class Property(PropertyBase):
    id:int
    agent_id:int
    images:List[PropertyImageOut]

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

# def form_json_deserializer(schema: Type[Serialized], 
#                            title:str  = Form(...),
#                            description:str  = Form(...),
#                            price:float = Form(...),
#                            country:str  = Form(...),
#                            city:str  = Form(...),
#                            street_address:str =Form(...),
#                            property_type:str =Form(...),
#                            advert_type:str =Form(...),
#                            num_of_rooms:str =Form(...),
#                            ) -> Serialized:
    
#     try:
#         return schema.parse_raw(title)
#     except ValidationError as e: 
#         raise HTTPException(detail=jsonable_encoder(e.errors()), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    
