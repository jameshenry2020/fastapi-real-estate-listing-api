import sqlalchemy as sql
from sqlalchemy_utils import URLType, PhoneNumberType
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from .database import Base
from sqlalchemy_utils import force_auto_coercion


force_auto_coercion()


class User(Base):
    __tablename__ = "users"
    id=sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    email=sql.Column(sql.String(255), unique=True, index=True)
    password=sql.Column(sql.String)
    is_active=sql.Column(sql.Boolean, server_default='TRUE')
    is_verified=sql.Column(sql.Boolean, default=False)
    date_joined=sql.Column(sql.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    profile = relationship("AgentDetails", uselist=False, back_populates="user")


class UserOneTimePassword(Base):
    __tablename__ = "user_otp"
    id=sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    user_id=sql.Column(sql.Integer, sql.ForeignKey("users.id", ondelete="CASCADE"))
    code=sql.Column(sql.String(6), unique=True, nullable=False)
    is_valid=sql.Column(sql.Boolean, default=True)
    


class AgentDetails(Base):
    __tablename__="agent_details"
    id=sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    full_name=sql.Column(sql.String)
    office_address=sql.Column(sql.String)
    phone_number=sql.Column(sql.String(20), PhoneNumberType())
    profile_img=sql.Column(sql.String,  nullable=True) #url of the uploaded file
    user_id=sql.Column(sql.Integer, sql.ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", uselist=False, back_populates="profile")


#define properties models
class Property(Base):
    __tablename__="properties"
    id=sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    title=sql.Column(sql.String, nullable=False)
    description=sql.Column(sql.String, nullable=False)
    price=sql.Column(sql.Float, nullable=False)
    country=sql.Column(sql.String)
    city=sql.Column(sql.String, nullable=False)
    street_address=sql.Column(sql.String, nullable=False)
    property_type=sql.Column(sql.String, nullable=False) # office, commercial, apartment
    advert_type=sql.Column(sql.String, nullable=False) #for sale or rent
    num_of_rooms=sql.Column(sql.Integer, nullable=False, default=0)
    agent_id=sql.Column(sql.Integer, sql.ForeignKey("agent_details.id"))
    availability_status=sql.Column(sql.Boolean, default=True) # still open or taken
    date_listed=sql.Column(sql.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    thumbnail=sql.Column(sql.String, URLType(), nullable=True)
    images = relationship("PropertyImages",  back_populates="property")

#define properties images
class PropertyImages(Base):
    __tablename__="property_images"
    id=sql.Column(sql.Integer, primary_key=True, autoincrement=True, index=True)
    property_id=sql.Column(sql.Integer, sql.ForeignKey("properties.id"))
    img_url=sql.Column(sql.String, URLType(), nullable=False)
    property=relationship("Property", back_populates="images")


#agent review models