import sqlite3 as sq
import re
from datetime import datetime
from create_bot import bot

r = re.compile('[^a-zA-Z]')

def sql_start():
    global r
    global base, cur
    try:
        base = sq.connect('Finance_bot.db')
        cur = base.cursor()
        if base:
            print("Succsed")
    except Exception as ex:
        print("nadazdelac")
        print(ex)

async def sql_add_table(user):
    try:
        base.execute('CREATE TABLE IF NOT EXISTS ' + user + '(obj, price, description, time, data)')
        base.commit()
    except Exception as ex:
        print("nadazdelac")
        print(ex) 

async def sql_add_row(user, obj, price, description):
    try:
        now = datetime.now()
        dt_string_data = now.strftime("%Y-%m-%d")
        dt_string_time = now.strftime("%H:%M:%S")
        cur.execute('INSERT INTO ' + user + ' VALUES (?,?,?,?,?)', (obj,price,description,dt_string_time,dt_string_data))
        base.commit()
    except Exception as ex:
        print("nadazdelac v db")
        print(ex)


async def return_data_from_db_by_callback(callback, date):
    user = 'U'+str(callback.from_user.id)
    try:
        data = cur.execute("SELECT * FROM " + user + " WHERE data == '" + str(date) + "'").fetchall()
        if len(data) == 0:
            await callback.message.answer('У вас немає записів за цю дату')
        else:
            for row in data:
                await callback.message.answer(f'Object: {row[0]}\nPrice: {row[1]}\nDecription: {row[2]}\nTime: {row[3]}, Data: {row[4]}')
    except:
        await callback.answer('Шось пішло не так, перевірте правильність написання дати.')
            
async def return_data_from_db_by_message(message):
    user = 'U'+str(message.from_user.id)
    try:
        data = cur.execute("SELECT * FROM " + user + " WHERE data == '" + str(message.text) + "'").fetchall()
        if len(data) == 0:
            await bot.send_message(message.from_user.id, 'У вас немає записів за цю дату')
        else:
            for row in data:
                await bot.send_message(message.from_user.id, f'Object: {row[0]}\nPrice: {row[1]}\nDecription: {row[2]}\nTime: {row[3]}, Data: {row[4]}')
    except:
        await bot.send_message(message.from_user.id, 'Шось пішло не так, перевірте правильність написання дати.')

async def print_sum(callback, data, previous_data):
    user = 'U'+str(callback.from_user.id)
    final_price = 0
    try:
        for price in cur.execute("SELECT price FROM " + user + " WHERE data BETWEEN '" + previous_data +"' and '" + data +"'"):
            final_price += price[0]
        await bot.send_message(callback.from_user.id, f'Сума ваших витрат та прибутків = {final_price}')
    except Exception as ex:
        print(ex)
        await bot.send_message(callback.from_user.id, 'Шось пішло не так при обрахуванні суми витрат за місяць')

