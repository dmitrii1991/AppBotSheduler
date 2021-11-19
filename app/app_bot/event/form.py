from aiogram.dispatcher.filters.state import State, StatesGroup


from app_bot.form import MyStatesGroup


class FormEventDelete(MyStatesGroup):
    id: State = State()


class FormEventDeleteName(FormEventDelete):
    ...


class FormEvent(MyStatesGroup):
    name: State = State()
    type_event: State = State()
    repetition: State = State()
    date: State = State()
    days_reminder: State = State()


class FormEditEvent(MyStatesGroup):
    id: State = State()
    name: State = State()
    type_event: State = State()
    repetition: State = State()
    date: State = State()
    days_reminder: State = State()
