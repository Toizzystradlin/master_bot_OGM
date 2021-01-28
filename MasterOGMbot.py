import mysql.connector
import telebot
import re
import json

import Send_message
from datetime import datetime

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='12345',
    port='3306',
    database='ogm2'
)
cursor = db.cursor(buffered=True)
bot = telebot.TeleBot('#')
# bot.send_message(392674056, 'бип боп')

MQuery = {}

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'choose':              # вывод кнопок со списком сотрудников из таблицы бд
        try:
            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            MQuery['query_id'] = msg[0]
            print(MQuery['query_id'])

            sql = "SELECT * FROM employees WHERE (master = 'False')"
            cursor.execute(sql)
            emps = cursor.fetchall()

            for emp in emps:
                keyboard = telebot.types.InlineKeyboardMarkup()
                key_1 = telebot.types.InlineKeyboardButton(emp[1], callback_data='choose_man')
                keyboard.add(key_1)
                bot.send_message(call.message.chat.id, '*id: *' + str(emp[0]) + "\n" + '*ФИО: *' + emp[1] + "\n" + '*Должность: *' + emp[2], reply_markup=keyboard, parse_mode="Markdown")
        except:
            print('ошибка в чуз')

    elif call.data == 'choose_man':
        try:
            ids = re.findall(r'\d+', call.message.text)  # блок считывания id сотрудника
            MQuery['employee_id'] = ids[0]
            print(MQuery['employee_id'])

            sql = "SELECT fio, tg_id FROM employees WHERE employee_id = %s"
            val = (MQuery['employee_id'],)
            cursor.execute(sql, val)
            fio = cursor.fetchone()

            doers = []
            doers.append(MQuery['employee_id'])
            doers_dict = {'doers': doers}
            doers_json = json.dumps(doers_dict)

            sql = "UPDATE queries SET json_emp = %s, query_status = %s WHERE query_id = %s"  # назначение сотрудника
            val = (doers_json, 'Принята', MQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            keyboard = telebot.types.InlineKeyboardMarkup()
            key_1 = telebot.types.InlineKeyboardButton("Да", callback_data='choose_more')
            keyboard.add(key_1)
            key_2 = telebot.types.InlineKeyboardButton("Нет", callback_data='sent')
            keyboard.add(key_2)
            bot.send_message(call.message.chat.id, fio[0] + ' назначен, назначить еще кого-то?', reply_markup=keyboard)

            #sql = "SELECT fio, tg_id FROM employees WHERE (employee_id = %s) LIMIT 0, 1"
            #val = (MQuery['employee_id'],)
            #cursor.execute(sql, val)
            #man = cursor.fetchone()
#
            #Send_message.send_message_3(MQuery['query_id'])  # выводит мастеру инфо о заявке
            #bot.send_message(call.message.chat.id, 'заявка отправлена исполнителю: ' + man[0])
            #bot.delete_message(call.message.chat.id, message_id=call.message.message_id - 1)
            Send_message.send_message_2(fio[1], MQuery['query_id'])  # отправка исполнителю
            #bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        except:
            print('ошибка в чуз мэн')

    elif call.data == 'choose_more':
        sql = "SELECT * FROM employees WHERE (master = 'False')"
        cursor.execute(sql)
        emps = cursor.fetchall()

        sql = "SELECT json_emp FROM queries WHERE query_id = %s"            # получение json
        val = (MQuery['query_id'],)
        cursor.execute(sql, val)
        json_emp = cursor.fetchone()[0]
        json_emp_dict = json.loads(json_emp)
        json_emp_list = json_emp_dict['doers']
        print(type(json_emp_list[0]))

        for i in emps:
            print(type(i[0]))
            if i[0] != int(json_emp_list[0]):
                keyboard = telebot.types.InlineKeyboardMarkup()
                key_1 = telebot.types.InlineKeyboardButton(i[1], callback_data='choose_man_more')
                keyboard.add(key_1)
                bot.send_message(call.message.chat.id,
                                 '*id: *' + str(i[0]) + "\n" + '*ФИО: *' + i[1] + "\n" + '*Должность: *' + i[2],
                                 reply_markup=keyboard, parse_mode="Markdown")

    elif call.data == 'choose_man_more':
        ids = re.findall(r'\d+', call.message.text)  # блок считывания id сотрудника
        MQuery['employee_id'] = ids[0]

        sql = "SELECT fio, tg_id FROM employees WHERE employee_id = %s"
        val = (MQuery['employee_id'],)
        cursor.execute(sql, val)
        fio = cursor.fetchone()

        sql = "SELECT json_emp FROM queries WHERE query_id = %s"   # получение json
        val = (MQuery['query_id'],)
        cursor.execute(sql, val)
        json_emp = cursor.fetchone()[0]
        json_emp_dict = json.loads(json_emp)
        doers = json_emp_dict['doers']

        doers.append(MQuery['employee_id'])
        doers_dict = {'doers': doers}
        doers_json = json.dumps(doers_dict)

        sql = "UPDATE queries SET json_emp = %s, query_status = %s WHERE query_id = %s"  # назначение сотрудника
        val = (doers_json, 'принята', MQuery['query_id'])
        cursor.execute(sql, val)
        db.commit()

        Send_message.send_message_2(fio[1], MQuery['query_id'])  # отправка исполнителю

        keyboard = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton("Да", callback_data='choose_more')
        keyboard.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton("Нет", callback_data='sent')
        keyboard.add(key_2)
        bot.send_message(call.message.chat.id, fio[0] + ' назначен, назначить еще кого-то?', reply_markup=keyboard)


    elif call.data == 'postpone':             # отложить заявку
        try:
            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            MQuery['query_id'] = msg[0]
            sql = "UPDATE queries SET query_status = %s WHERE query_id = %s"
            val = ('Отложена исполнителем', MQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()
            Send_message.send_message_3(MQuery['query_id'])  # выводит мастеру инфо о заявке
            bot.send_message(call.message.chat.id, 'Заявка отложена')
            bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        except:
            print('ошибка в постпоне')

    elif call.data == 'new_queries':
        try:
            sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                  "queries.reason, queries.msg, queries.query_id FROM " \
                  "equipment JOIN queries ON ((queries.eq_id = equipment.eq_id) AND (" \
                  "queries.query_status = 'Новая')) "

            cursor.execute(sql,)
            my_queries = cursor.fetchall()
            print(my_queries)
            if len(my_queries) == 0:
                bot.send_message(call.message.chat.id, 'Новых заявок нет')
            else:
                bot.send_message(call.message.chat.id, 'Новые заявки:')
            for query in my_queries:
                keyboard = telebot.types.InlineKeyboardMarkup()
                key_choose = telebot.types.InlineKeyboardButton('Назначить ...', callback_data='choose')
                keyboard.add(key_choose)
                key_postpone = telebot.types.InlineKeyboardButton('Отложить', callback_data='postpone')
                keyboard.add(key_postpone)
                bot.send_message(call.message.chat.id,
                                   '*Id заявки: *' + str(query[6]) + "\n" + '*Наименование: *' + str(
                                       query[0]) + "\n" + "*Инв.№: *" + str(query[1]) + "\n" +
                                   "*Тип: *" + str(query[2]) + "\n" + "*Участок: *" + query[
                                       3] + "\n" + "*Причина поломки: *" +
                                   query[4] + "\n" + "*Сообщение: *" + str(query[5]), reply_markup=keyboard,
                                   parse_mode="Markdown")
        except: pass

    elif call.data == 'postpone_queries':
        try:
            sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                  "queries.reason, queries.msg, queries.query_id FROM " \
                  "equipment JOIN queries ON ((queries.eq_id = equipment.eq_id) AND (" \
                  "queries.query_status = 'Отложена мастером')) "

            cursor.execute(sql, )
            my_queries = cursor.fetchall()
            print(my_queries)
            if len(my_queries) == 0:
                bot.send_message(call.message.chat.id, 'Отложенных заявок нет')
            else:
                bot.send_message(call.message.chat.id, 'Отложенные заявки:')

            for query in my_queries:
                keyboard = telebot.types.InlineKeyboardMarkup()
                key_choose = telebot.types.InlineKeyboardButton('Назначить ...', callback_data='choose')
                keyboard.add(key_choose)
                key_postpone = telebot.types.InlineKeyboardButton('Отложить', callback_data='postpone')
                keyboard.add(key_postpone)
                bot.send_message(call.message.chat.id,
                                 '*Id заявки: *' + str(query[6]) + "\n" + '*Наименование: *' + str(
                                     query[0]) + "\n" + "*Инв.№: *" + str(query[1]) + "\n" +
                                 "*Тип: *" + str(query[2]) + "\n" + "*Участок: *" + query[
                                     3] + "\n" + "*Причина поломки: *" +
                                 query[4] + "\n" + "*Сообщение: *" + str(query[5]), reply_markup=keyboard,
                                 parse_mode="Markdown")
        except:
            pass

    elif call.data == 'sent':
        bot.send_message(call.message.chat.id, 'Сотрудники назначены')


@bot.message_handler(commands=['menu'])
def handle_commands(message):
    if message.text == '/menu':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton('Новые заявки', callback_data='new_queries')
        keyboard.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton('Отложенные заявки', callback_data='postpone_queries')
        keyboard.add(key_2)
        bot.send_message(message.chat.id, 'Меню', reply_markup=keyboard)
    else:
        None
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
