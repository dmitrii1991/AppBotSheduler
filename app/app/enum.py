from enum import Enum


class BasEnum(str, Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class TypeEventEnum(BasEnum):
    BIRTH = "BIRTHDATE"
    DOC = "DOCUMENT"
    EVENT = "EVENT"


class RepetitionEventEnum(BasEnum):
    NONE = "NONE"
    MONTH = "MONTH"
    YEAR = "YEAR"
