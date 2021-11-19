import pytest
from loguru import logger
import nest_asyncio
from aiogram.types import ReplyKeyboardMarkup

from settings import config
from app.utils import Secret, JWT
from app.enum import *
from app_bot.utils import Validator, replay_markup_3

config["extra"]["WORKER"] = "PyTest_unit"
logger.configure(**config)
nest_asyncio.apply()


@pytest.mark.unit
class TestAPP:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_secret(self):
        password = Secret.get_new_password()
        pw = Secret.hashpw(password)
        assert Secret.checkpw(password, pw.decode())

    @pytest.mark.asyncio
    async def test_jwt(self):
        token = JWT.create_access_token({"ed": "ed"})
        assert "ed" == JWT.decode(token)["ed"]


@pytest.mark.unit
class TestAppBot:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_validator_email(self):
        assert Validator.email_validator("2323@2ee.ru")
        assert not Validator.email_validator("222332323")

    @pytest.mark.asyncio
    async def test_validator_birthdate(self):
        assert Validator.birthdate_validator("10.12.1991")
        assert not Validator.birthdate_validator("2323232323")
        assert not Validator.birthdate_validator("10.12.9999")

    @pytest.mark.asyncio
    async def test_validator_phone_validator(self):
        assert not Validator.phone_validator("10.12.1991")
        assert Validator.phone_validator("2323232323")

    @pytest.mark.asyncio
    async def test_validator_type_enum_validator(self):
        assert Validator.type_enum_validator("BIRTHDATE", TypeEventEnum)
        assert not Validator.type_enum_validator("2323232323", TypeEventEnum)
        assert Validator.type_enum_validator("NONE", RepetitionEventEnum)
        assert not Validator.type_enum_validator("WEEKWEEK", RepetitionEventEnum)

    @pytest.mark.asyncio
    async def test_validator_event_date_validator(self):
        assert not Validator.event_date_validator("10.10.1991")
        assert not Validator.event_date_validator("10.120.1991")
        assert Validator.event_date_validator("10.10.9999")
        assert Validator.event_date_validator("10.10.1991", birthdate=True)
        assert not Validator.event_date_validator("10.10.9999", birthdate=True)
        assert not Validator.event_date_validator("10.120.1991", birthdate=True)

    @pytest.mark.asyncio
    async def test_validator_int_segment_validator(self):
        assert Validator.int_segment_validator("4", 0, 6)
        assert not Validator.int_segment_validator("10", 0, 6)

    @pytest.mark.asyncio
    async def test_replay_markup_3(self):
        for enum in [TypeEventEnum, RepetitionEventEnum]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            replay_markup_3(markup, enum)
            assert markup.conf == {"row_width": 3}
            keyboard = markup.values["keyboard"]
            num_list = enum.list()
            num_list.append("cancel")
            for i, row in enumerate(keyboard):
                assert row == num_list[i*3:3+i*3]


@pytest.mark.unit
class TestAppSheduler:
    """Checking basic models"""
    ...
