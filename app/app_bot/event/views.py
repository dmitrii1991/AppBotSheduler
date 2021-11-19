from os.path import join
from os import remove

from aiogram.types import ParseMode, Message, User, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.markdown import bold, text
from aiogram.utils.exceptions import BadRequest

from .keyboard import KB_EVENT_ENG, KB_EVENT_RUS, KB_EVENT_DEL_RUS, KB_EVENT_DEL_ENG
from .form import *

from app_bot import bot
from settings import MAX_FREE_EVENTS, MAX_PAY_EVENTS, API_URL, LOGS_DIR
from app.models import UserTortModel, EventTortModel


async def process_event_main(message: Message):
    user: User = message.from_user
    if user.language_code == "ru":
        await message.reply("Панель управления событиями", reply_markup=KB_EVENT_RUS)
    else:
        await message.reply(f"Events dashboard", reply_markup=KB_EVENT_ENG)


async def process_create_event(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    user_bd: UserTortModel = await UserTortModel.get(teleg_id=callback_query.from_user.id)
    events_bd = await EventTortModel.all().filter(user=user_bd)
    if not user_bd.subscription:
        if len(events_bd) >= MAX_FREE_EVENTS:
            if callback_query.from_user.language_code == "ru":
                return await bot.send_message(
                    callback_query.from_user.id,
                    text('Исчерпан лимит для бесплатных событий ', bold(f'{MAX_FREE_EVENTS}')),
                    parse_mode=ParseMode.MARKDOWN)
            else:
                return await bot.send_message(
                    callback_query.from_user.id,
                    text('The limit for free events has been reached ', bold(f'{MAX_FREE_EVENTS}')),
                    parse_mode=ParseMode.MARKDOWN)
    else:
        if len(events_bd) >= MAX_PAY_EVENTS:
            if callback_query.from_user.language_code == "ru":
                return await bot.send_message(
                    callback_query.from_user.id,
                    text('Исчерпан лимит для платных событий ', bold(f'{MAX_PAY_EVENTS}')),
                    parse_mode=ParseMode.MARKDOWN)
            else:
                return await bot.send_message(
                    callback_query.from_user.id,
                    text('The limit for pay events has been reached ', bold(f'{MAX_PAY_EVENTS}')),
                    parse_mode=ParseMode.MARKDOWN)

    await FormEvent.name.set()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row('cancel')

    if callback_query.from_user.language_code == "ru":
        await bot.send_message(
            callback_query.from_user.id,
            text('Название события? Напишете для отмены ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)
    else:
        await bot.send_message(
            callback_query.from_user.id,
            text('The name of the event? Write to ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)


async def process_list_event(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_bd: UserTortModel = await UserTortModel.get(teleg_id=callback_query.from_user.id)
    events_bd = await EventTortModel.all().filter(user=user_bd)
    text2 = ''
    if not events_bd:
        text2 = "None events"
    else:
        for event_bd in events_bd:
            event_bd = await event_bd
            text2 += text(
                f"{bold('id')}: {event_bd.id} {bold('type')}: {event_bd.type_event} {bold('date')}: {event_bd.date}\n"
                f"{bold('name')}: {event_bd.name if len(event_bd.name) < 40 else event_bd.name[:37] + '...'}\n"
                f"{bold('repertion')}: {event_bd.repetition} {bold('date reminder')}: {event_bd.date_reminder}\n"
                f"{'-'*40}\n")
    try:
        await callback_query.message.edit_text(
            text2, parse_mode=ParseMode.MARKDOWN, reply_markup=KB_EVENT_RUS)
    except BadRequest:
        await callback_query.message.edit_text(
            "Ответ слишком большой. Отправляем файл!" if callback_query.from_user.language_code == "ru" else
            "The answer is too big. Sending the file",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=KB_EVENT_RUS if callback_query.from_user.language_code == "ru" else KB_EVENT_ENG)
        path_file = join(LOGS_DIR, f"{callback_query.from_user.id}.txt")
        with open(path_file, "w") as file:
            file.write(text2)
        await bot.send_document(callback_query.from_user.id, open(path_file, "rb"))
        remove(path_file)


async def process_del_event(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.language_code == "ru":
        await callback_query.message.edit_text(
            "Прошу выбрать опции для удаления",
            parse_mode=ParseMode.MARKDOWN, reply_markup=KB_EVENT_DEL_RUS)
    else:
        await callback_query.message.edit_text(
            "Прошу выбрать опции для удаления",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=KB_EVENT_DEL_ENG)


async def process_info_event(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.language_code == "ru":
        message_text = text(
            'Функционал приложение', bold(' "Заметок"\n'),
            'Бот будет напоминать каждый день о назначенном событии за определенное время, которое Вы выбрали.\n',
            'При выборе BIRTHDATE срок повторения будет ежегодно по умолчанию\n',
            f'Управление API {API_URL}'
        )
        await callback_query.message.edit_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN, reply_markup=KB_EVENT_RUS)
    else:
        message_text = text(
            '   Application functionality', bold(' "Notes"'), '\n',
            '  The bot will remind you every day about the scheduled event for a certain time that you have chosen.\n',
            '  When selected', bold("BIRTHDATE"), ' the repetition period will be yearly by default\n',
            f'  API Management {API_URL}'
        )
        await callback_query.message.edit_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN, reply_markup=KB_EVENT_ENG)


async def process_close_event(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


async def process_del_event_by_id(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.from_user.language_code == "ru":
        await callback_query.message.edit_text(
            "Прошу выбрать опции для удаления",
            parse_mode=ParseMode.MARKDOWN, reply_markup=KB_EVENT_DEL_RUS)
    else:
        await callback_query.message.edit_text(
            "Please select the options to delete",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=KB_EVENT_DEL_ENG)


async def process_del_event_id(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    await FormEventDelete.id.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("cancel")

    if callback_query.from_user.language_code == "ru":
        await bot.send_message(
            callback_query.from_user.id,
            "Введите номер id заметки, или введите их через запятую (Пробелы не учитываются!)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)
    else:
        await bot.send_message(
            callback_query.from_user.id,
            "Enter the id number of the note, or enter them separated by commas (Spaces are not taken into account!)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)


async def process_del_event_name(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    await FormEventDeleteName.id.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("cancel")

    if callback_query.from_user.language_code == "ru":
        await bot.send_message(
            callback_query.from_user.id,
            "Введите название (или часть названия) заметки (Удаление происходит по Одному! Если название будет в "
            "нескольких заметках, то они удалятся!)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)
    else:
        await bot.send_message(
            callback_query.from_user.id,
            "Enter the name (or part of the name) of the note (Deletion occurs one at a time! If the name is in "
            "a few notes, then they will be deleted!)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)


async def process_del_event_all(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user: User = callback_query.from_user
    user_bd: UserTortModel = await UserTortModel.get(teleg_id=user.id)
    deleted = await EventTortModel.filter(user=user_bd).delete()
    ok = False
    if deleted:
        ok = True
    if user.language_code == "ru":
        await callback_query.message.edit_text(
            text("Удаление всех событий ", bold(f"ПРОИЗВЕДЕНО"), "\n",
                  f"УСПЕШНО удалено {deleted}" if ok else "НЕУСПЕШНО"),
            reply_markup=KB_EVENT_RUS,
            parse_mode=ParseMode.MARKDOWN)
    else:
        await callback_query.message.edit_text(
            text("Deleting events by name ", bold(f"PRODUCED"), "\n",
                  f"SUCCESSFULLY deleted {deleted}" if ok else "UNSUCCESSFUL"),
            reply_markup=KB_EVENT_DEL_ENG,
            parse_mode=ParseMode.MARKDOWN)


async def process_event_back(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user: User = callback_query.from_user
    if user.language_code == "ru":
        await callback_query.message.edit_text("Панель управления событиями.", reply_markup=KB_EVENT_RUS)
    else:
        await callback_query.message.edit_text(f"Events dashboard.", reply_markup=KB_EVENT_ENG)
