from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

b_out = InlineKeyboardButton(text = 'Вивести📋', callback_data="Вивести")
b_in = InlineKeyboardButton(text = 'Записати🖊️', callback_data="Додати")

b_today = InlineKeyboardButton(text = 'Вивести за сьогодні📆', callback_data="Сьогодні")
b_tomorow = InlineKeyboardButton(text = 'Вивести за вчора📆', callback_data="Вчора")
b_month = InlineKeyboardButton(text = 'Вивести за попередній місяць📆', callback_data="Місяць")
b_date = InlineKeyboardButton(text = 'Своя дата📆', callback_data="Дата")

start_kb_client = InlineKeyboardMarkup(row_width=2)
out_kb_client =InlineKeyboardMarkup(row_width=1)

start_kb_client.add(b_in, b_out)
out_kb_client.add(b_today, b_tomorow, b_month, b_date)