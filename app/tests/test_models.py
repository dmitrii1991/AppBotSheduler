
import datetime

import pytest
from loguru import logger
import nest_asyncio

from .utils import DateExamples
from app.models import EventTortModel, UserTortModel
from app.enum import *
from app.errors import TortDateFieldException
from settings import TEST_DB_URL, config

config["extra"]["WORKER"] = "PyTest_models"
logger.configure(**config)
nest_asyncio.apply()

today = datetime.datetime.now().date()
# logger.info(birth.date)


@pytest.mark.models
class TestUnitModelsEvent:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_event_tort_model_error_birthdate(self):
        user = await UserTortModel.all().first()
        with pytest.raises(TortDateFieldException):
            await EventTortModel.create(
                name="ДР",
                type_event=TypeEventEnum.BIRTH,
                date=today + datetime.timedelta(days=10),
                days_reminder=10, user=user)

    @pytest.mark.asyncio
    async def test_event_tort_model_error_event_doc(self):
        user = await UserTortModel.all().first()
        with pytest.raises(TortDateFieldException):
            await EventTortModel.create(
                name="EVENT",
                type_event=TypeEventEnum.EVENT,
                date=today - datetime.timedelta(days=10),
                days_reminder=10, user=user)
        with pytest.raises(TortDateFieldException):
            await EventTortModel.create(
                name="EVENT",
                type_event=TypeEventEnum.DOC,
                date=today - datetime.timedelta(days=10),
                days_reminder=10, user=user)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("birth", [
        DateExamples(today.replace(year=today.year - 20), today),
        DateExamples(today.replace(year=today.year - 25), today)])
    async def test_event_tort_model_birthdate_today(self, birth):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.BIRTH,
            date=birth.date,
            days_reminder=10, user=user)
        assert event.repetition == RepetitionEventEnum.YEAR, f"Repeatability error BIRTH={birth.date} REP={10}"
        assert event.date_reminder == birth.answer, f"Date reminder error BIRTH={birth.date} REP={10}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("birth", [
        DateExamples(datetime.date(1995, 12, 25),
                     datetime.date(1995, 12, 25).replace(year=today.year) - datetime.timedelta(days=10)),
        DateExamples(datetime.date(1995, 1, 2),
                     datetime.date(1995, 1, 2).replace(year=today.year + 1) - datetime.timedelta(days=10)),
    ])
    async def test_event_tort_model_birthdate_lessday(self, birth):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.BIRTH,
            date=birth.date,
            days_reminder=10, user=user)
        assert event.repetition == RepetitionEventEnum.YEAR, f"Repeatability error BIRTH={birth.date} REP={10}"
        assert event.date_reminder == birth.answer, f"Date reminder error BIRTH={birth.date} REP={10}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("event_", [
        DateExamples(today + datetime.timedelta(days=10), today),
        DateExamples(today + datetime.timedelta(days=5), today),
        DateExamples(today + datetime.timedelta(days=30), today + datetime.timedelta(days=20)),
    ])
    async def test_event_tort_model_event_lessday(self, event_):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.DOC,
            date=event_.date,
            days_reminder=10, user=user)
        assert event.repetition == RepetitionEventEnum.YEAR, f"Repeatability error EVENT={event_.date} EVENT={10}"
        assert event.date_reminder == event_.answer, f"Date reminder error EVENT={event_.date} EVENT={10}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("event_", [
        DateExamples(today + datetime.timedelta(days=10), today),
        DateExamples(today + datetime.timedelta(days=5), today),
        DateExamples(today + datetime.timedelta(days=20), today + datetime.timedelta(days=10)),
    ])
    async def test_event_tort_model_event_steps(self, event_):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.DOC,
            date=event_.date,
            days_reminder=10, user=user)
        assert event.repetition == RepetitionEventEnum.YEAR, f"Repeatability error EVENT={event_.date} EVENT={10}"
        assert event.date_reminder == event_.answer, f"Date reminder error EVENT={event_.date} EVENT={10}"
        days = (event_.date - event_.answer).days
        for _ in range(days):
            await event.next_step()
            event_.answer += datetime.timedelta(days=1)
            assert event.date_reminder == event_.answer, f"Date reminder error EVENT={event_.date} E_rem={event.date_reminder} EVENT={10}"
        await event.next_step()
        assert event.date_reminder == event_.answer.replace(year=today.year+1) - datetime.timedelta(days=10), f"Date reminder error EVENT={event_.date} E_rem={event.date_reminder} EVENT={10}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("birth", [
        DateExamples(today.replace(year=today.year - 20), today),
    ])
    async def test_event_tort_model_birth_steps(self, birth):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.BIRTH,
            date=birth.date,
            days_reminder=10, user=user)
        assert event.repetition == RepetitionEventEnum.YEAR, f"Repeatability error BIRTH={birth.date} EVENT={10}"
        assert event.date_reminder == birth.answer, f"Date reminder error BIRTH={birth.date} E_rem={event.date_reminder} EVENT={10}"
        await event.next_step()
        assert event.date_reminder == today.replace(year=today.year+1) - datetime.timedelta(days=10), f"Date reminder error BIRTH={birth.date} E_rem={event.date_reminder} EVENT={10}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("birth", [
        DateExamples(datetime.date(1995, 12, 31),
                     datetime.date(1995, 12, 31).replace(year=today.year) - datetime.timedelta(days=10)),
        DateExamples(datetime.date(1995, 1, 1),
                     datetime.date(1995, 1, 1).replace(year=today.year + 1) - datetime.timedelta(days=10)),
    ])
    async def test_event_tort_model_birth_steps2(self, birth):
        user = await UserTortModel.all().first()
        event = await EventTortModel.create(
            name="ДР",
            type_event=TypeEventEnum.BIRTH,
            date=birth.date,
            days_reminder=10, user=user)
        for _ in range(10):
            await event.next_step()
            birth.answer += datetime.timedelta(days=1)
            assert event.date_reminder == birth.answer, f"Date reminder error EVENT={birth.date} " \
                                                        f"E_rem={event.date_reminder} EVENT={10}"
        await event.next_step()
        assert event.date_reminder == birth.answer.replace(year=birth.answer.year + 1) - datetime.timedelta(
            days=10), f"Date reminder error EVENT={birth.date} E_rem={event.date_reminder} EVENT={10}"
