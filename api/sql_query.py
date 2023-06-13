from sqlalchemy.orm import Session
from . import models, schema


def check_user_exist(db:Session, email: str):
    user=db.query(models.User).filter(models.User.email == email).first()
    return user

def get_user_by_id(db:Session, user_id:int):
     return db.query(models.User).filter(models.User.id == user_id).first()

def get_agent_by_id(db, agent_id:int):
    return db.query(models.AgentDetails).filter(models.AgentDetails.id == agent_id).first()

def get_all_agents(db:Session):
    return db.query(models.AgentDetails).all()

def insert_new_user(db:Session, user:schema.UserCreate):
    db_user = models.User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_otp_for_user(db:Session, otp:schema.OTPData):
    db_otp = models.UserOneTimePassword(user_id=otp.user_id, code=otp.code)
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def create_new_property(db:Session, property:schema.PropertyBase, imgurl, agent_id):
    db_property = models.Property(agent_id=agent_id, thumbnail=imgurl, **property.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def add_image_to_property(db:Session, property_id, imgUrl):
    db_property_image = models.PropertyImages(property_id=property_id, img_url=imgUrl)
    db.add(db_property_image)
    db.commit()
    db.refresh(db_property_image)
    return db_property_image
    







