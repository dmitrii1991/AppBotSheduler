from aiogram import Dispatcher

from .views import *
from .form_logic import *
from app_bot import dp
from app_bot.utils import Validator


def register_event_menu(dp: Dispatcher):
    dp.register_message_handler(process_event_main, commands='event')

    dp.register_callback_query_handler(process_create_event, lambda c: c.data == 'create_event')
    dp.register_callback_query_handler(process_list_event, lambda c: c.data == 'list_event')
    dp.register_callback_query_handler(process_del_event, lambda c: c.data == 'del_event')
    dp.register_callback_query_handler(process_info_event, lambda c: c.data == 'info_event')
    dp.register_callback_query_handler(process_close_event, lambda c: c.data == 'close_event')


def register_del_event_menu(dp: Dispatcher):
    dp.register_callback_query_handler(process_del_event_id, lambda c: c.data == 'del_event_id')
    dp.register_message_handler(form_del_event_id, state=FormEventDelete.id)

    dp.register_callback_query_handler(process_del_event_name, lambda c: c.data == 'del_event_name')
    dp.register_message_handler(form_del_event_name, state=FormEventDeleteName.id)

    dp.register_callback_query_handler(process_del_event_all, lambda c: c.data == 'del_event_all')
    dp.register_callback_query_handler(process_event_back, lambda c: c.data == 'event_back')


def register_create_event(dp: Dispatcher):
    dp.register_message_handler(process_event_name, state=FormEvent.name)

    dp.register_message_handler(process_validate_type_event,
        lambda message: not Validator.type_enum_validator(message.text, TypeEventEnum),
        state=FormEvent.type_event)
    dp.register_message_handler(process_type_event, state=FormEvent.type_event)

    dp.register_message_handler(process_validate_repetition,
        lambda message: not Validator.type_enum_validator(message.text, RepetitionEventEnum),
        state=FormEvent.repetition)
    dp.register_message_handler(process_repetition, state=FormEvent.repetition)

    dp.register_message_handler(process_event_date, state=FormEvent.date)

    dp.register_message_handler(process_event_validate_days_reminder,
        lambda message: not Validator.int_segment_validator(message.text, 0, 31),
        state=FormEvent.days_reminder)
    dp.register_message_handler(process_event_days_reminder, state=FormEvent.days_reminder)


def register_edit_event(dp: Dispatcher):
    dp.register_message_handler(process_event_name, state=FormEvent.name)

    dp.register_message_handler(process_validate_type_event,
        lambda message: not Validator.type_enum_validator(message.text, TypeEventEnum),
        state=FormEvent.type_event)
    dp.register_message_handler(process_type_event, state=FormEvent.type_event)

    dp.register_message_handler(process_validate_repetition,
        lambda message: not Validator.type_enum_validator(message.text, RepetitionEventEnum),
        state=FormEvent.repetition)
    dp.register_message_handler(process_repetition, state=FormEvent.repetition)

    dp.register_message_handler(process_event_validate_date,
        lambda message: not Validator.event_date_validator(message.text),
        state=FormEvent.date)
    dp.register_message_handler(process_event_date, state=FormEvent.date)

    dp.register_message_handler(process_event_validate_days_reminder,
        lambda message: not Validator.int_segment_validator(message.text, 0, 6),
        state=FormEvent.days_reminder)
    dp.register_message_handler(process_event_days_reminder, state=FormEvent.days_reminder)


register_event_menu(dp)
register_create_event(dp)
register_del_event_menu(dp)
