from pydantic import PydanticValueError
from tortoise.exceptions import BaseORMException


class PydanticNullError(PydanticValueError):
    code = 'null'
    msg_template = 'You cannot give value "{wrong_value}"'


class PydanticEnumError(PydanticValueError):
    code = 'enum_error'
    msg_template = '"{wrong_value}" not in "{enum_list}"'


class TortDateFieldException(BaseORMException):
    ...
