import datetime

from aiogram.types import Message, User, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import bold, text

from .form import FormEvent
from .keyboard import KB_EVENT_ENG, KB_EVENT_RUS, KB_EVENT_DEL_RUS, KB_EVENT_DEL_ENG
from app_bot import bot
from app_bot.utils import replay_markup_3, unmarkup, Validator
from app.models import UserTortModel, EventTortModel
from app.enum import TypeEventEnum, RepetitionEventEnum


async def process_event_name(message: Message, state: FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        data['name'] = message.text
    await FormEvent.next()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    replay_markup_3(markup, TypeEventEnum)
    if user.language_code == "ru":
        await message.reply(
            text('Тип события? Напишете для отмены ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)
    else:
        await message.reply(
            text('Type of event? Write to cancel ', bold('cancel')),
            reply_markup=markup)


async def process_validate_type_event(message: Message):
    user = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Выбирете тип события из предложенных ниже позиций!")
    else:
        return await message.reply(f"Choose the type of event from the positions suggested below!")


async def process_type_event(message: Message, state: FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        data['type_event'] = message.text
        if data['type_event'] == "BIRTHDATE":
            data['repetition'] = RepetitionEventEnum.YEAR
            await FormEvent.through_next()
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.row('cancel')
            if user.language_code == "ru":
                await message.reply(
                    text('Напищите дату события. Напишете для отмены ', bold('cancel')),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)
            else:
                await message.reply(
                    text('Write the date of the event. Write to cancel ', bold('cancel')),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)
        else:
            await FormEvent.next()
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            replay_markup_3(markup, RepetitionEventEnum)
            if user.language_code == "ru":
                await message.reply(
                    text('Выберите повторяемость событий. Напишете для отмены ', bold('cancel')),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)
            else:
                await message.reply(
                    text('Choose the repeatability of events. Write to cancel ', bold('cancel')),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)


async def process_validate_repetition(message: Message):
    user = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Выбирете тип события из предложенных ниже позиций!")
    else:
        return await message.reply(f"Choose the type of event from the positions suggested below!")


async def process_repetition(message: Message, state: FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        data['repetition'] = message.text
    await FormEvent.next()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row('cancel')
    if user.language_code == "ru":
        await message.reply(
            text('Напищите дату события. Напишете для отмены ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)
    else:
        await message.reply(
            text('Write the date of the event. Write to cancel ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup)


async def process_event_validate_date(message: Message):
    user: UserTortModel = message.from_user
    if user.language_code == "ru":
        return await message.reply(
            "Дата дня события должна быть в формате формат (ДД.ММ.ГГГГ) или больше текущей даты или None")
    else:
        return await message.reply(
            "The date of the day of the event must be in the format (DD.MM.YYYY) or greater than the current date or None")


async def process_event_date(message: Message, state: FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        if not Validator.event_date_validator(message.text, True if data['type_event'] == "BIRTHDATE" else False):
            if user.language_code == "ru":
                return await message.reply(
                    "Дата дня события должна быть в формате формат (ДД.ММ.ГГГГ) или больше текущей даты (Если ДР, то наоборот)")
            else:
                return await message.reply(
                    "The date of the day of the event must be in the format (DD.MM.YYYY) or greater than the current date")
        text_list = message.text.split('.')
        data['date'] = datetime.date(day=int(text_list[0]), month=int(text_list[1]), year=int(text_list[2]))
    await FormEvent.next()
    if user.language_code == "ru":
        await message.reply(
            text('За сколько дней начать напоминать Вам? (выбирете число от 1 до 5). Напишете для отмены ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply(
            text('How many days will it take to start reminding you? (choose a number from 1 to 5). Write to cancel ', bold('cancel')),
            parse_mode=ParseMode.MARKDOWN)


async def process_event_validate_days_reminder(message: Message):
    user: UserTortModel = message.from_user
    if user.language_code == "ru":
        return await message.reply(
            "Выбирете число от 1 до 5")
    else:
        return await message.reply(
            "Choose a number from 1 to 5")


async def process_event_days_reminder(message: Message, state: FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        data['days_reminder'] = int(message.text)

        user_bd: UserTortModel = await UserTortModel.get(teleg_id=user.id)
        await EventTortModel.create(**data, user=user_bd)
        await state.finish()
        markup = ReplyKeyboardRemove()
        if user.language_code == "ru":
            await message.reply(text("Спасибо за составление Событие ", bold(f"{data.get('name')}")),
                                reply_markup=markup,
                                parse_mode=ParseMode.MARKDOWN)
            await bot.send_message(message.chat.id, "Возвращение в меню.", reply_markup=KB_EVENT_RUS)
        else:
            await message.reply(text("Thank you for creating a EventTortModel ", bold(f"{data.get('name')}")),
                                reply_markup=markup,
                                parse_mode=ParseMode.MARKDOWN)
            await bot.send_message(message.chat.id, "Return to the menu", reply_markup=KB_EVENT_ENG)


# --------------------------------


async def form_del_event_id(message: Message, state: FSMContext):
    user: User = message.from_user
    ids: str = message.text.replace(" ", "")
    ids: set = set(ids.split(','))
    ok, wrong = [], []
    if ids:
        user_bd: UserTortModel = await UserTortModel.get(teleg_id=user.id)
        for id_ in ids:
            try:
                deleted = await EventTortModel.filter(user=user_bd, id=id_).delete()
            except:
                deleted = 0
            if deleted:
                ok.append(id_)
            else:
                wrong.append(id_)
    await state.finish()
    if user.language_code == "ru":
        await message.reply(
            text("Удаление событий по id ", bold(f"ПРОИЗВЕДЕНО"), "\n",
                 f"УСПЕШНО {', '.join(ok)} \n",
                 f"НЕУСПЕШНО {', '.join(wrong)} \n"),
            reply_markup=unmarkup,
            parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(message.chat.id, "Возвращение в меню", reply_markup=KB_EVENT_DEL_RUS)
    else:
        await message.reply(
            text("Deleting events by id ", bold(f"PRODUCED"), "\n",
                 f"SUCCESSFUL {', '.join(ok)} \n",
                 f"UNSUCCESSFUL {', '.join(wrong)} \n"),
            reply_markup=KB_EVENT_DEL_ENG,
            parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(message.chat.id, "Return to the menu", reply_markup=KB_EVENT_DEL_ENG)


async def form_del_event_name(message: Message, state: FSMContext):
    user: User = message.from_user
    name: str = message.text
    ok = False
    user_bd: UserTortModel = await UserTortModel.get(teleg_id=user.id)
    deleted = await EventTortModel.filter(user=user_bd, name__contains=name).delete()
    if deleted:
        ok = True
    await state.finish()
    if user.language_code == "ru":
        await message.reply(
            text("Удаление событий по имени ", bold(f"ПРОИЗВЕДЕНО"), "\n",
                  f"УСПЕШНО удалено {deleted}" if ok else "НЕУСПЕШНО"),
            reply_markup=unmarkup,
            parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(message.chat.id, "Возвращение в меню", reply_markup=KB_EVENT_DEL_RUS)
    else:
        await message.reply(
            text("Deleting events by name ", bold(f"PRODUCED"), "\n",
                  f"SUCCESSFULLY deleted {deleted}" if ok else "UNSUCCESSFUL"),
            reply_markup=unmarkup,
            parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(message.chat.id, "Return to the menu", reply_markup=KB_EVENT_DEL_ENG)
