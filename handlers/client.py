from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from data_base import sql_db
from keyboards import start_kb_client, out_kb_client
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class FSMClient(StatesGroup):
    obj = State()
    price = State()
    description = State()

class FSMReturn(StatesGroup):
    data_for_show = State()


# Старт
async def comands_start(message : types.Message):
    await sql_db.sql_add_table(user='U'+str(message.from_user.id))
    await bot.send_message(message.from_user.id, 'Початок роботи.', reply_markup=start_kb_client)

# Наводимо приклад опису речі
async def comands_help(message : types.Message):
    await message.answer("Введіть будь ласка ОДНУ річ або подію, на яку ви витралити кошти, а також кількість витрачених на неї кошт.\nБот опитавє вас, вам потрібно буде просто відповісти на його питання і він сам запише все що ви сказали.")
    await message.answer("Приклад: \nОбєкт: Крісло \nЦіна: -13000 \nОпис: Купив, геймерське крісло Dxracer master max. Мені зробили знижку через відсутність оригінальної подушки.")

# Початок зчитування подій
async def cm_start(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await FSMClient.obj.set()
    await callback_query.message.answer('Що за річ/подія?')

# Зчитуємо назву
async def load_obj(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['obj'] = message.text
    await FSMClient.next()
    await message.reply('Тепер введи ціну(якщо витратив став - перед ціною, якщо ж заробив +)')

# Зчитуємо ціну
async def load_price(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = float(message.text)
    await FSMClient.next()
    await message.reply('Тепер можеш коротко описати цю річ/подію')

# Зчитуємо допис
async def load_description(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMClient.next()
    name = 'U'+str(message.from_user.id)
    await message.answer('Обробляю данні')
    try:
        await message.answer(f"Name: {name}\nObject: {data['obj']}\nPrice: {data['price']}\nDecription: {data['description']}")
        await sql_db.sql_add_row(user=name,obj=data['obj'], price=data['price'], description=data['description'])
        await message.answer('Дані успішно надійшли на сервер.')
        await message.answer('Що робимо далі?', reply_markup=start_kb_client)
    except:
        await message.answer('Щось пішло не так при загрузі ваших даних на сервер.')
    await state.finish()


# Вихід зі стану 
async def cancel_hand(message : types.Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state is None:
        return 
    await state.finish()
    await message.reply('OK')


#Вибор виводу
async def choose_for_output(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text='Оберіть період: ', reply_markup=out_kb_client) 

#Вивід вчорашніх записів
async def cm_show_from_tomorow(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer("Виводжу записи за вчора:")
    await sql_db.return_data_from_db_by_callback(callback_query, datetime.now().date() - timedelta(days=1))
    await callback_query.message.answer('Що робимо далі?', reply_markup=start_kb_client)

#Вивід сьогоднішніх записів
async def cm_show_from_today(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer("Виводжу записи за сьогодні:")
    await sql_db.return_data_from_db_by_callback(callback_query, datetime.now().date())
    await callback_query.message.answer('Що робимо далі?', reply_markup=start_kb_client)

async def cm_show_from_month(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer("Виводжу записи за місяць:")
    await sql_db.print_sum(callback_query, str(datetime.now().date()), str(datetime.now().date() - relativedelta(month=1)))
    await callback_query.message.answer('Що робимо далі?', reply_markup=start_kb_client)


async def cm_show_by_date(callback_query: types.CallbackQuery):
    await FSMReturn.data_for_show.set()
    await callback_query.message.delete()
    await callback_query.message.answer('Введіть дату у форматі (рік-місяц-день) для перегляду витрат та прибутуків за цю дату')


async def ask_data(message: types.Message, state: FSMContext):
    await FSMReturn.next()
    await message.reply('Поняв')
    await sql_db.return_data_from_db_by_message(message)
    await message.answer('Що робимо далі?', reply_markup=start_kb_client)
    await state.finish()


# Оголошуємо та привязуємо команди до функцій
def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(comands_help, commands=['help'])
    dp.register_message_handler(comands_start, commands=['start'])

    dp.register_callback_query_handler(cm_start, text="Додати", state=None)
    dp.register_message_handler(load_obj, state=FSMClient.obj)
    dp.register_message_handler(load_price, state=FSMClient.price)
    dp.register_message_handler(load_description, state=FSMClient.description)

    dp.register_message_handler(cancel_hand, state="*", commands='відміна')
    dp.register_message_handler(cancel_hand, Text(equals='відміна', ignore_case='True'), state='*')

    dp.register_callback_query_handler(choose_for_output, text="Вивести")
    dp.register_message_handler(ask_data, state=FSMReturn.data_for_show)
    dp.register_callback_query_handler(cm_show_from_tomorow, text="Вчора")
    dp.register_callback_query_handler(cm_show_from_today, text="Сьогодні")
    dp.register_callback_query_handler(cm_show_from_month, text="Місяць")
    dp.register_callback_query_handler(cm_show_by_date, text="Дата")