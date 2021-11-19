from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inl_but_create_event_rus = InlineKeyboardButton('Создать', callback_data='create_event')
inl_but_list_event_rus = InlineKeyboardButton('Список', callback_data='list_event')
inl_but_del_event_rus = InlineKeyboardButton('Удалить', callback_data='del_event')
inl_but_upd_event_rus = InlineKeyboardButton('Редактировать', callback_data='upd_event')
inl_but_info_event_rus = InlineKeyboardButton('Инфо', callback_data='info_event')
inl_but_exit_rus = InlineKeyboardButton('Выход', callback_data='close_event')

kb_event_rus = InlineKeyboardMarkup(one_time_keyboard=True).row(
    inl_but_create_event_rus, inl_but_list_event_rus, inl_but_del_event_rus)
KB_EVENT_RUS = kb_event_rus.row(
    inl_but_upd_event_rus, inl_but_info_event_rus, inl_but_exit_rus)

inl_but_create_event_eng = InlineKeyboardButton('Create', callback_data='create_event')
inl_but_list_event_eng = InlineKeyboardButton('List', callback_data='list_event')
inl_but_del_event_eng = InlineKeyboardButton('Delete', callback_data='del_event')
inl_but_upd_event_eng = InlineKeyboardButton('Update', callback_data='upd_event')
inl_but_info_event_eng = InlineKeyboardButton('Info', callback_data='info_event')
inl_but_exit_eng = InlineKeyboardButton('Exit', callback_data='close_event')

kb_event_eng = InlineKeyboardMarkup(one_time_keyboard=True).row(
    inl_but_create_event_eng, inl_but_list_event_eng, inl_but_del_event_eng)
KB_EVENT_ENG = kb_event_eng.row(
    inl_but_upd_event_eng, inl_but_info_event_eng, inl_but_exit_eng)

# -----------------------------------------------------------------------------------------

inl_but_del_event_id_rus = InlineKeyboardButton('Удалить по id', callback_data='del_event_id')
inl_but_del_event_name_rus = InlineKeyboardButton('Удалить по названию', callback_data='del_event_name')
inl_but_del_event_all_rus = InlineKeyboardButton('Удалить все', callback_data='del_event_all')
inl_but_event_back_rus = InlineKeyboardButton('Назад в меню', callback_data='event_back')

kb_event_del_rus = InlineKeyboardMarkup(one_time_keyboard=True).row(
    inl_but_del_event_id_rus, inl_but_del_event_name_rus)
KB_EVENT_DEL_RUS = kb_event_del_rus.row(
    inl_but_del_event_all_rus, inl_but_event_back_rus)

inl_but_del_event_id_eng = InlineKeyboardButton('Delete by id', callback_data='del_event_id')
inl_but_del_event_name_eng = InlineKeyboardButton('Delete by name', callback_data='del_event_name')
inl_but_del_event_all_eng = InlineKeyboardButton('Delete all', callback_data='del_event_all')
inl_but_event_back_eng = InlineKeyboardButton('Back to the menu', callback_data='event_back')

kb_event_del_eng = InlineKeyboardMarkup(one_time_keyboard=True).row(
    inl_but_del_event_id_eng, inl_but_del_event_name_eng)
KB_EVENT_DEL_ENG = kb_event_del_eng.row(
    inl_but_del_event_all_eng, inl_but_event_back_eng)
