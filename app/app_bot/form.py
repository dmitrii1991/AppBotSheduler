from datetime import date

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup, Dispatcher

from app_bot import dp
from app_bot.utils import Validator
from app.models import UserTortModel


class MyStatesGroup(StatesGroup):
    @classmethod
    async def through_next(cls) -> str:
        state = Dispatcher.get_current().current_state()
        state_name = await state.get_state()

        try:
            next_step = cls.states_names.index(state_name) + 2
        except ValueError:
            next_step = 0

        try:
            next_state_name = cls.states[next_step].state
        except IndexError:
            next_state_name = None

        await state.set_state(next_state_name)
        return next_state_name


class FormUser(MyStatesGroup):
    firstname: State = State()
    patronymic: State = State()
    lastname: State = State()
    birthdate: State = State()
    email: State = State()
    phone: State = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: not message.text.isalpha(), state=FormUser.firstname)
async def process_validate_firstname(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Имя должно состоять из букв")
    else:
        return await message.reply(f"The firstname must consist of letters")


@dp.message_handler(state=FormUser.firstname)
async def process_firstname(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['firstname'] = message.text
    await FormUser.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("None")
    if user.language_code == "ru":
        await message.reply(f"Как твоё Отчество?", reply_markup=markup)
    else:
        await message.reply(f"What's your patronymic?", reply_markup=markup)


@dp.message_handler(lambda message: not message.text.isalpha(), state=FormUser.patronymic)
async def process_validate_patronymic(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Отчество должно состоять из букв")
    else:
        return await message.reply(f"The patronymic must consist of letters")


@dp.message_handler(state=FormUser.patronymic)
async def process_patronymic(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['patronymic'] = message.text
    await FormUser.next()
    if user.language_code == "ru":
        await message.reply(f"Как твоя фамилия?")
    else:
        await message.reply(f"What's your lastname?")


@dp.message_handler(lambda message: not message.text.isalpha(), state=FormUser.lastname)
async def process_validate_lastname(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Фамилия должно состоять из букв")
    else:
        return await message.reply(f"The lastname must consist of letters")


@dp.message_handler(state=FormUser.lastname)
async def process_lastname(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['lastname'] = message.text
    await FormUser.next()
    if user.language_code == "ru":
        await message.reply(f"Когда твой день рождения формат (ДД.ММ.ГГГГ)?")
    else:
        await message.reply(f"What's your birthdate? (DD.MM.YY)")


@dp.message_handler(lambda message: not Validator.birthdate_validator(message.text, ['None']), state=FormUser.birthdate)
async def process_validate_birthdate(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Дата дня рождения должен быть в формате формат (ДД.ММ.ГГГГ) или None")
    else:
        return await message.reply(f"The date of the birthday must be in the format format (DD.MM.YYYY) or None")


@dp.message_handler(state=FormUser.birthdate)
async def process_birthdate(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['birthdate'] = message.text
    await FormUser.next()
    unmarkup = types.ReplyKeyboardRemove()
    if user.language_code == "ru":
        await message.reply(f"Какая твоя почта?", reply_markup=unmarkup)
    else:
        await message.reply(f"What's your email?", reply_markup=unmarkup)


@dp.message_handler(lambda message: not Validator.email_validator(message.text), state=FormUser.email)
async def process_check_email(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Почта не имеет валидный формат")
    else:
        return await message.reply(f"The mail does not have a valid format")


@dp.message_handler(state=FormUser.email)
async def process_email(message: types.Message, state: FSMContext):
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['email'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("None")
    await FormUser.next()
    if user.language_code == "ru":
        await message.reply(f"Твой номер телефона", reply_markup=markup)
    else:
        await message.reply(f"What's your phone?)", reply_markup=markup)


@dp.message_handler(lambda message: not Validator.phone_validator(message.text, ['None']), state=FormUser.phone)
async def process_age_invalid(message: types.Message):
    user: types.User = message.from_user
    if user.language_code == "ru":
        return await message.reply(f"Телефон не имеет валидный формат")
    else:
        return await message.reply(f"The phone does not have a valid format")


@dp.message_handler(state=FormUser.phone)
async def process_phone(message: types.Message, state: FSMContext):
    unmarkup: types.ReplyKeyboardRemove = types.ReplyKeyboardRemove()
    user: types.User = message.from_user
    async with state.proxy() as data:
        data['phone'] = message.text

    update: dict = {}
    for key, value in data.items():
        if value != 'None':
            if key == 'birthdate':
                text_list = value.split('.')
                update[key] = date(day=int(text_list[0]), month=int(text_list[1]), year=int(text_list[2]))
            else:
                update[key] = value
    user_bd: UserTortModel = await UserTortModel.get(teleg_id=user.id)
    await user_bd.update_from_dict(update)
    await user_bd.save()
    if user.language_code == "ru":
        await message.reply(f"Спасибо за составление профиля!", reply_markup=unmarkup)
    else:
        await message.reply(f"Thank you for creating a profile!", reply_markup=unmarkup)
    await state.finish()
