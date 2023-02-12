from aiogram.utils import executor
from create_bot import dp
from data_base import sql_db



async def on_startup(_):
    print("Бота запушено успішно")
    sql_db.sql_start()


from handlers import client

client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)