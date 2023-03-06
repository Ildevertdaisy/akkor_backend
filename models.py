from enum import Enum
from bson import ObjectId
from typing import Optional

from pydantic import EmailStr, Field, BaseModel, validator

from email_validator import validate_email, EmailNotValidError

from datetime import date, datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}


class Role(str, Enum):

    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class UserBase(MongoBaseModel):

    username: str = Field(..., min_length=3, max_length=15)
    email: str = Field(...)
    password: str = Field(...)
    role: Role

    @validator("email")
    def valid_email(cls, v):

        try:
            email = validate_email(v).email
            return email
        except EmailNotValidError as e:

            raise EmailNotValidError


class UserUpdate(MongoBaseModel):
    email : Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginBase(BaseModel):
    email: str = EmailStr(...)
    password: str = Field(...)


class CurrentUser(BaseModel):
    email: str = EmailStr(...)
    username: str = Field(...)
    role: str = Field(...)


class HotelBase(MongoBaseModel):
    name: str
    location: str
    description: str
    picture_list: list[str]


class HotelDB(HotelBase):
    owner: str = Field(...)


class HotelUpdate(MongoBaseModel):
    name: Optional[str] = None
    location: Optional[str] = None 
    description: Optional[str] = None
    picture_list: Optional[list[str]] = None

class BookingBase(MongoBaseModel):
    start_date: date
    end_date: date
    hotel_id: str = Field(...)


# class BookingDB(BookingBase):
#     customer: str = Field(...)

class BookingDB(MongoBaseModel):
    start_date: str
    end_date: str
    hotel_id: str = Field(...)
    customer: str = Field(...)