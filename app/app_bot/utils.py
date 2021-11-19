import re
from datetime import date, datetime
from typing import Optional, Union

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from pydantic import validate_email
from pydantic.errors import EmailError

from app.enum import BasEnum


unmarkup = ReplyKeyboardRemove()


class Validator:

    @classmethod
    def email_validator(cls, text: str) -> bool:
        try:
            validate_email(text)
            return True
        except EmailError:
            return False

    @classmethod
    def birthdate_validator(cls, text: str, alt: Optional[list] = None) -> bool:
        if alt:
            if text in alt:
                return True
        text = re.search("(\d\d.\d\d.\d\d\d\d)", text)
        if not text:
            return False
        try:
            text_list = text.group(0).split('.')
            birthdate = date(day=int(text_list[0]), month=int(text_list[1]), year=int(text_list[2]))
            if birthdate < datetime.now().date():
                return True
            return False
        except:
            return False

    @classmethod
    def phone_validator(cls, text: str, alt: Optional[list] = None) -> bool:
        if alt:
            if text in alt:
                return True
        if text.isdigit():
            return True
        return False

    @classmethod
    def type_enum_validator(cls, text: str, enum: BasEnum) -> bool:
        if text in {i for i in enum.list()}:
            return True
        return False

    @classmethod
    def event_date_validator(cls, text: str, birthdate=False) -> bool:
        text = re.search("(\d\d.\d\d.\d\d\d\d)", text)
        if not text:
            return False
        try:
            text_list = text.group(0).split('.')
            date_event = date(day=int(text_list[0]), month=int(text_list[1]), year=int(text_list[2]))
            if not birthdate:
                if date_event >= datetime.now().date():
                    return True
                return False
            else:
                if date_event >= datetime.now().date():
                    return False
                return True
        except:
            return False

    @classmethod
    def int_segment_validator(cls, text: str, ge: int, le: int) -> bool:
        if text.isalpha():
            return False
        if le > int(text) > ge:
            return True
        return False


def replay_markup_3(markup: ReplyKeyboardMarkup, enum, new: Union[list, str] = 'cancel'):
    elements: list = enum.list()
    if isinstance(new, str):
        elements.append(new)
    else:
        elements.extend(new)
    row = []
    for el in elements:
        row.append(el)
        if len(row) == 3:
            markup.row(*row)
            row = []
    else:
        if row:
            markup.row(*row)
