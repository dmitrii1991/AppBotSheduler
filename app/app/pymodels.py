from typing import Optional, List
import datetime

from pydantic import BaseModel, validator, Field, root_validator
from pydantic import validate_email
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import UserTortModel, EventTortModel
from app.errors import PydanticNullError, PydanticEnumError
from app.enum import TypeEventEnum, RepetitionEventEnum


class Status(BaseModel):
    message: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str


class UserUpdate(pydantic_model_creator(
    UserTortModel,
    name="UserUpdate",
    exclude=("teleg_id", "teleg_is_bot", "teleg_first_name", "token_hash", "teleg_username", "teleg_lang", "teleg_status",
             "token_created_at", "deactivate", "deactivate_at", "modified_at", "created_at", "is_test", "is_admin",
             "subscription", "subscription_end")
)):
    username: Optional[str] = Field(min_length=3, description="username")
    firstname: Optional[str]= Field(min_length=3, description="firstname")
    surname: Optional[str] = Field(min_length=3, description="sirname")
    lastname: Optional[str] = Field(min_length=3, description="lastname")

    @validator("username", "firstname", "patronymic", "lastname", "birthdate", "email", "phone")
    def validate_field(cls, value):
        if not value or value == "null":
            raise PydanticNullError(wrong_value=value)
        return value

    @validator('email')
    def validate_email_(cls, value):
        validate_email(value)
        return value


class UserMinimum(pydantic_model_creator(
    UserTortModel,
    name="UserMinimum",
    exclude=("username", "firstname", "patronymic", "lastname", "birthdate", "email", "phone", "password_hash",
             "token_hash", "token_created_at", "created_at", "modified_at", "deactivate", "deactivate_at", "is_test", "is_admin"),
    computed=("full_name",)
)):
    ...


class EventInfo(pydantic_model_creator(EventTortModel, name="EventInfo")):
    date: datetime.date = Field(description="EventTortModel date")


class EventCreate(pydantic_model_creator(EventTortModel, name="EventCreate", exclude=("id", "date_reminder"), )):
    days_reminder: int = Field(default=3, ge=0,  le=31, description="Days before the start of the reminder")
    name: str = Field(min_length=3, description="EventTortModel name")

    @validator("type_event")
    def type_event_enum(cls, value):
        if value not in TypeEventEnum.list():
            raise PydanticEnumError(wrong_value=value, enum_list=TypeEventEnum.list())
        return value

    @validator("repetition")
    def repetition_enum(cls, value):
        if value not in RepetitionEventEnum.list():
            raise PydanticEnumError(wrong_value=value, enum_list=TypeEventEnum.list())
        return value

    # @root_validator
    # def check_passwords_match(cls, values):
    #     pw1, pw2 = values.get('password1'), values.get('password2')
    #     if pw1 is not None and pw2 is not None and pw1 != pw2:
    #         raise ValueError('passwords do not match')
    #     return values


class UserGlobal(pydantic_model_creator(
    UserTortModel,
    name="UserGlobal",
    exclude=("token_hash", "token_created_at", "modified_at", "created_at")
)):
    ...


class UserMe(UserGlobal):
    events: List[EventInfo]
