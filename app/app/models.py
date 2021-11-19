from datetime import timedelta, date, datetime
from typing import Optional

from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from app.enum import *
from app.errors import TortDateFieldException


class FieldMixin:
    @classmethod
    def model_fields(cls):
        self = cls.__new__(cls)
        return self._meta.db_fields

    def fields(self):
        return {field: getattr(self, field) for field in self._meta.db_fields}


class EventTortModel(FieldMixin, Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(null=False, max_length=255, description='EventTortModel name')
    # see about fields.CharEnumField https://github.com/tortoise/tortoise-orm/issues/601
    type_event: TypeEventEnum = fields.CharEnumField(TypeEventEnum, default=TypeEventEnum.EVENT, max_length=10, description=f"type event: ENUM IN {TypeEventEnum.list()}")
    repetition: RepetitionEventEnum = fields.CharEnumField(RepetitionEventEnum, default=RepetitionEventEnum.YEAR, description=f"repetition: ENUM IN {RepetitionEventEnum.list()}")
    date = fields.DateField(null=False, description='EventTortModel date')
    days_reminder: int = fields.SmallIntField(default=3, description='Days before the start of the reminder')
    date_reminder = fields.DateField(description="date reminder trace")

    user: fields.ForeignKeyRelation["UserTortModel"] = fields.ForeignKeyField("models.UserTortModel", related_name="events")

    class Meta:
        table = "event"
        table_description = "This table contains the dates of various events for reminders"

    def __str__(self):
        return self.name

    @property
    def days(self) -> int:
        if self.type_event == "BIRTHDATE":
            return (date(day=self.date.day, month=self.date.month, year=datetime.now().year) - datetime.now().date()).days
        return abs((datetime.now().date() - self.date).days)

    async def save(self, *args, **kwargs) -> None:
        if self.date_reminder is None:
            today = datetime.now().date()
            delta_rem = timedelta(days=self.days_reminder)
            if self.type_event == "BIRTHDATE":
                if self.date > today:
                    raise TortDateFieldException('The date of birth cannot be greater than the current date')
                birth = date(day=self.date.day, month=self.date.month, year=today.year)
                if birth >= today:
                    if birth - delta_rem >= today:
                        self.date_reminder = birth - delta_rem
                    else:
                        self.date_reminder = today
                else:
                    if date(day=self.date.day, month=self.date.month, year=today.year+1) - delta_rem >= today:
                        self.date_reminder = date(day=self.date.day, month=self.date.month, year=today.year+1) - delta_rem
                    else:
                        self.date_reminder = date(day=self.date.day, month=self.date.month, year=today.year+1)
            else:
                if self.date < today:
                    raise TortDateFieldException(f'date must not be {self.date} - less then {today} type_event: {self.type_event}')
                if self.date - delta_rem >= today:
                    self.date_reminder = self.date - delta_rem
                else:
                    self.date_reminder = today
        await super().save(*args, **kwargs)

    async def next_step(self, *args, **kwargs) -> None:
        today = datetime.now().date()
        if self.type_event != "BIRTHDATE":
            if self.date == self.date_reminder:
                if self.repetition == RepetitionEventEnum.YEAR:
                    self.date_reminder = self.date.replace(year=self.date.year + 1) - timedelta(days=self.days_reminder)
                elif self.repetition == RepetitionEventEnum.MONTH:
                    if self.date.month != 12:
                        self.date_reminder = self.date.replace(month=self.date.month + 1) - timedelta(days=self.days_reminder)
                    else:
                        self.date_reminder = self.date.replace(year=self.date.year + 1, month=1) - timedelta(days=self.days_reminder)
            else:
                self.date_reminder += timedelta(days=1)
        else:
            date_ = self.date.replace(today.year)
            if today > date_:
                date_ = date_.replace(date_.year + 1)
            if date_ == self.date_reminder:
                if self.repetition == RepetitionEventEnum.YEAR:
                    self.date_reminder = date_.replace(year=date_.year + 1) - timedelta(days=self.days_reminder)
                elif self.repetition == RepetitionEventEnum.MONTH:
                    if date_.month != 12:
                        self.date_reminder = date_.replace(month=date_.month + 1) - timedelta(days=self.days_reminder)
                    else:
                        self.date_reminder = date_.replace(year=date_.year + 1, month=1) - timedelta(days=self.days_reminder)
            else:
                self.date_reminder += timedelta(days=1)
        await super().save(*args, **kwargs)

    @classmethod
    async def update_self(cls, event_id: int, data: "EventCreate") -> None:
        today = datetime.now().date()
        event = await cls.get(id=event_id)
        name = event.name if "name" not in data.dict().keys() else data.dict()["name"]
        type_event = event.type_event if "type_event" not in data.dict().keys() else data.dict()["type_event"]
        repetition = event.repetition if "repetition" not in data.dict().keys() else data.dict()["repetition"]
        date_ = event.repetition if "date" not in data.dict().keys() else data.dict()["date"]
        days_reminder = event.days_reminder if "days_reminder" not in data.dict().keys() else data.dict()["days_reminder"]
        delta_rem = timedelta(days=days_reminder)

        if type_event == "BIRTHDATE":
            if date_ > today:
                raise TortDateFieldException('The date of birth cannot be greater than the current date')
            birth = date(day=date_.day, month=date_.month, year=today.year)
            if birth >= today:
                if birth - delta_rem >= today:
                    date_reminder = birth - delta_rem
                else:
                    date_reminder = today
            else:
                if date(day=date_.day, month=date_.month, year=today.year + 1) - delta_rem >= today:
                    date_reminder = date(day=date_.day, month=date_.month, year=today.year + 1) - delta_rem
                else:
                    date_reminder = date(day=date_.day, month=date_.month, year=today.year + 1)
        else:
            if date_ < today:
                raise TortDateFieldException(f'date must not be {date_} - less then {today} type_event: {type_event}')
            if date_ - delta_rem >= today:
                date_reminder = date_ - delta_rem
            else:
                date_reminder = today

        await cls.filter(id=event_id).update(**{
            "name": name,
            "type_event": type_event,
            "repetition": repetition,
            "date": date_,
            "days_reminder": days_reminder,
            "date_reminder": date_reminder,
        })


class UserTortModel(FieldMixin, Model):
    id = fields.IntField(pk=True)

    teleg_id = fields.IntField(unique=True, description='ID Telegram')
    teleg_is_bot = fields.BooleanField(default=False, description='Telegram bot')
    teleg_first_name = fields.CharField(null=True, max_length=255, description='Telegram first name')
    teleg_username = fields.CharField(null=True, max_length=255, description='Telegram username')
    teleg_lang = fields.CharField(null=True, max_length=15, description='Telegram language')
    teleg_status = fields.CharField(default="active", max_length=10, description='active')

    username = fields.CharField(null=True, unique=True, max_length=255, description='username unique')
    firstname = fields.CharField(null=True, max_length=255, description='firstname')
    patronymic = fields.CharField(null=True, max_length=255, description='sirname')
    lastname = fields.CharField(null=True, max_length=255, description='lastname')
    birthdate = fields.DateField(null=True, description='birthdate')
    email = fields.CharField(max_length=255, null=True, unique=True, description='email')
    phone = fields.CharField(max_length=11, null=True, unique=True, description='phone')
    password_hash = fields.CharField(max_length=255, null=True, description='hash password')
    token_hash = fields.CharField(max_length=255, null=True, description='hash token')
    token_created_at = fields.DatetimeField(null=True, description='created date token')

    created_at = fields.DatetimeField(auto_now_add=True, description='Дата создания')
    modified_at = fields.DatetimeField(auto_now=True, description='Дата обновления')
    deactivate = fields.BooleanField(default=False, description='Деактивирован ли профиль')
    deactivate_at = fields.DatetimeField(null=True, description='Дата создания')
    is_test = fields.BooleanField(default=False, description='Тестовый ли аккаунт')
    is_admin = fields.BooleanField(default=False, description='Имеет ли админские права')
    subscription = fields.BooleanField(default=False, description='Подписка')
    subscription_end = fields.DatetimeField(null=True, description='Конец подписки')

    events: fields.ReverseRelation["EventTortModel"]

    def full_name(self) -> str:
        if self.username or self.lastname:
            return f"{self.username or ''} {self.lastname or ''}".strip()
        return self.username

    class Meta:
        table = "user"
        table_description = "This table contains a list of all users"

    class PydanticMeta:
        exclude = ["password_hash", "token", "id"]

    def __str__(self):
        return f"{self.teleg_first_name}/{self.teleg_id}"

    async def update_self(self, data) -> "UserTortModel":
        await self.filter(id=self.id).update(**data.dict(exclude_unset=True))
        return self.id

    @classmethod
    async def get_by_email_or_none(cls, email: str) -> Optional["UserTortModel"]:
        try:
            query = cls.get_or_none(email=email)
            user = await query
            return user
        except DoesNotExist:
            return None
