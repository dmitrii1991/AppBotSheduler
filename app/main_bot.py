from os.path import join
from typing import Optional

from aiogram import executor, types
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import code, italic
from tortoise import Tortoise

from app.utils import Secret
from app_bot.form import FormUser
from app_bot.event import *
from settings import POSTGRESQL_URL, MEDIA_PATH
from app_bot import dp, bot


@dp.message_handler(commands="start")
async def start(message: types.Message):
    user: types.User = message.from_user
    user_bd: Optional[UserTortModel] = await UserTortModel.get_or_none(teleg_id=user.id)
    if not user_bd:
        password: bytes = Secret.get_new_password()
        hash_password: bytes = Secret.hashpw(password)
        await FormUser.firstname.set()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("None")
        await UserTortModel.create(
            teleg_id=user.id,
            teleg_is_bot=user.is_bot,
            teleg_first_name=user.first_name,
            teleg_username=user.full_name,
            teleg_lang=user.language_code,
            username=user.username,
            password_hash=hash_password.decode())
        if user.language_code == "ru":
            await message.reply(
                f"Добрый день {user.username}!\t"
                f"Твой пароль от сервисов {password.decode()}\t"
                f"Ответь на несколько необязательных вопросов для расширения профиля.\t"
                f" (Почта обязательна). Какое твое имя?",
                reply_markup=markup)
        else:
            await message.reply(
                f"Good afternoon {user.username}!\t"
                f"Your password from the services {password.decode()}\t"
                f"Answer a few optional questions to expand your profile..\t"
                f"(Mail is required). Hi there! What's your name?",
                reply_markup=markup)
    else:
        return await message.answer(
            emojize(f"Привет, {message.from_user.full_name} / id({message.from_user.id})"),
            parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands="help")
async def help(message: types.Message):
    message_text = text(
        italic('Список доступных команд/сервисов'), 'что есть\n',
        bold('Управление событиями'), code('команда'), '/event')
    await message.reply(message_text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_message(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        message_text = text(emojize('Я не знаю, что с этим делать :astonished:'),
                            italic('\nЯ просто напомню,'), 'что есть',
                            code('команда'), '/help')
    else:
        message_text = text(emojize('I do not know what to do with it  :astonished:'),
                            italic("\nI'll just remind you,"), 'what is',
                            code('command'), '/help')
    await message.reply(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())
    photo = open(join(MEDIA_PATH, "what_is_this.jpg"), 'rb')
    await bot.send_photo(message.chat.id, photo)


@dp.message_handler(content_types=["text"])
def default_test(message):
    id = message.chat.id
    bot.send_message(message.chat.id, f"Чат: {id}")


async def on_startup(dispatcher):
    await Tortoise.init(db_url=POSTGRESQL_URL, modules={"models": ["app.models"]})
    await dispatcher.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("event", "Событие"),
    ], language_code='ru'
    )


async def on_shutdown(dispatcher):
    await Tortoise.close_connections()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
