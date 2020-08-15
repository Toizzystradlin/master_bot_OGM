import mysql.connector
import telebot
import re
import json
from telebot import apihelper
import Send_message
from datetime import datetime

#apihelper.proxy = {'https':'https://51.158.111.229:8811'}  # рабочий прокси Франция
#apihelper.proxy = {'https':'192.168.0.100:50278'}  #
while True:
    try:

        n_emp = 0
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='12345',
            port='3306',
            database='ogm2'
        )
        cursor = db.cursor()
        bot = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')
        # bot.send_message(392674056, 'бип боп')

        MQuery = {}


        sql = "SELECT tg_id FROM employees WHERE master = '1'"
        cursor.execute(sql)
        allowed_users = cursor.fetchall()
        allowed_ids = []
        for i in allowed_users:
            allowed_ids.append(i[0])

        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == 'choose':              # вывод кнопок со списком сотрудников из таблицы бд
                try:
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor()

                    msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                    MQuery['query_id'] = msg[0]
                    print(MQuery['query_id'])

                    emp_id = call.message.chat.id  # блок выделения id сотрудника
                    sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                    val = (emp_id,)
                    cursor.execute(sql, val)
                    master_id = cursor.fetchone()[0]

                    sql = "SELECT query_status FROM queries WHERE query_id = %s"
                    val = (MQuery['query_id'],)
                    cursor.execute(sql, val)
                    status = cursor.fetchone()
                    if status[0] == 'Завершена':
                        bot.send_message(call.message.chat.id, 'Эта заявка уже завершена...')
                    else:
                        sql = "SELECT appointer FROM queries WHERE query_id = %s"
                        val = (MQuery['query_id'],)
                        cursor.execute(sql, val)
                        appointer = cursor.fetchone()
                        if appointer[0] == None or appointer[0] == master_id:
                            sql = "SELECT * FROM employees"
                            cursor.execute(sql,)
                            emps = cursor.fetchall()
                            print(emps)
                            for emp in emps:
                                keyboard = telebot.types.InlineKeyboardMarkup()
                                key_1 = telebot.types.InlineKeyboardButton(emp[1], callback_data='choose_man')
                                keyboard.add(key_1)
                                bot.send_message(call.message.chat.id, '*id: *' + str(emp[0]), reply_markup=keyboard, parse_mode="Markdown")
                        else:
                            bot.send_message(call.message.chat.id, 'На эту заявку уже назначены сотрудники')
                    keyboard = telebot.types.InlineKeyboardMarkup()

                    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                  message_id=call.message.message_id,
                                                  reply_markup=keyboard)
                except:
                    print('ошибка в чуз')

            elif call.data == 'choose_man':
                #try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor()
                emp_id = call.message.chat.id  # блок выделения id сотрудника
                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                master_id = cursor.fetchone()[0]
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
                sql = "UPDATE queries SET json_emp = %s, appointer = %s, query_status = %s WHERE query_id = %s"  # назначение сотрудника
                #val = (doers_json, master_id, 'Принята', MQuery['query_id'])
                val = (doers_json, master_id, 'Принята', MQuery['query_id'])
                cursor.execute(sql, val)
                db.commit()



                keyboard = telebot.types.InlineKeyboardMarkup()
                key_1 = telebot.types.InlineKeyboardButton("Да", callback_data='choose_more')
                keyboard.add(key_1)
                key_2 = telebot.types.InlineKeyboardButton("Нет", callback_data='sent')
                keyboard.add(key_2)
                bot.send_message(call.message.chat.id, fio[0] + ' назначен, назначить еще кого-то?', reply_markup=keyboard)
                Send_message.send_message_2(fio[1], MQuery['query_id'])  # отправка исполнителю
                #except:
                #    print('ошибка в чуз мэн')

            elif call.data == 'choose_more':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor()
                sql = "SELECT * FROM employees"
                cursor.execute(sql)
                emps = cursor.fetchall()

                sql = "SELECT json_emp FROM queries WHERE query_id = %s"            # получение json
                val = (MQuery['query_id'],)
                cursor.execute(sql, val)
                json_emp = cursor.fetchone()[0]
                json_emp_dict = json.loads(json_emp)
                json_emp_list = json_emp_dict['doers']
                print(type(json_emp_list[0]))

                sql = "SELECT * FROM employees"
                cursor.execute(sql, )
                empsn = cursor.fetchall()
                n = 0
                for emp in empsn:
                    n += 1
                    bot.delete_message(call.message.chat.id, call.message.message_id - n)

                for i in emps:
                    print(type(i[0]))
                    if i[0] != int(json_emp_list[0]):
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        key_1 = telebot.types.InlineKeyboardButton(i[1], callback_data='choose_man_more')
                        keyboard.add(key_1)
                        bot.send_message(call.message.chat.id,
                                         '*id: *' + str(i[0]),
                                         reply_markup=keyboard, parse_mode="Markdown")


            elif call.data == 'choose_man_more':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor()
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
                val = (doers_json, 'Принята', MQuery['query_id'])
                cursor.execute(sql, val)
                db.commit()

                #Send_message.send_message_2(fio[1], MQuery['query_id'])  # отправка исполнителю

                keyboard = telebot.types.InlineKeyboardMarkup()
                key_1 = telebot.types.InlineKeyboardButton("Да", callback_data='choose_more')
                keyboard.add(key_1)
                key_2 = telebot.types.InlineKeyboardButton("Нет", callback_data='sent')
                keyboard.add(key_2)
                bot.send_message(call.message.chat.id, fio[0] + ' назначен, назначить еще кого-то?', reply_markup=keyboard)


            elif call.data == 'postpone':             # отложить заявку
                try:
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor()
                    msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                    MQuery['query_id'] = msg[0]
                    sql = "UPDATE queries SET query_status = %s WHERE query_id = %s"
                    val = ('Отложена мастером', MQuery['query_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    Send_message.send_message_3(MQuery['query_id'])  # выводит мастеру инфо о заявке
                    bot.send_message(call.message.chat.id, 'Заявка отложена')
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                except:
                    print('ошибка в постпоне')

            elif call.data == 'new_queries':
                try:
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor()
                    sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                          "queries.reason, queries.msg, queries.query_id FROM " \
                          "queries JOIN equipment ON ((queries.eq_id = equipment.eq_id) AND (" \
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
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor()
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
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor()
                sql = "SELECT * FROM employees"
                cursor.execute(sql, )
                emps = cursor.fetchall()
                n = 0
                for emp in emps:
                    n += 1
                    bot.delete_message(call.message.chat.id, call.message.message_id - n)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                sql = "SELECT json_emp FROM queries WHERE query_id = %s"  # получение json
                val = (MQuery['query_id'],)
                cursor.execute(sql, val)
                json_emp = cursor.fetchone()[0]
                json_emp_dict = json.loads(json_emp)
                doers = json_emp_dict['doers']
                doers_string = ''
                for doer in doers:
                    cursor.execute('SELECT fio FROM employees WHERE employee_id = %s', [doer])
                    fio = cursor.fetchone()[0]
                    doers_string = doers_string + ' ' + fio
                bot.send_message(call.message.chat.id, 'Сотрудники назначены: ' + doers_string)


        @bot.message_handler(commands=['menu', 'task'])
        def handle_commands(message):
            if message.text == '/menu':
                emp_id = str(message.chat.id)
                if emp_id not in allowed_ids:
                    bot.send_message(message.chat.id, 'Вам не разрешено пользоваться этим ботом')
                else:
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('Новые заявки', callback_data='new_queries')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('Отложенные заявки', callback_data='postpone_queries')
                    keyboard.add(key_2)
                    bot.send_message(message.chat.id, 'Меню', reply_markup=keyboard)

            if message.text == '/task':
                emp_id = str(message.chat.id)
                if emp_id not in allowed_ids:
                    bot.send_message(message.chat.id, 'Вам не разрешено пользоваться этим ботом')
                else:
                    msg = bot.send_message(message.chat.id, 'Напишите задачи на день...')
                    bot.register_next_step_handler(msg, task)

        def task(message):
            tasks = message.text
            tasks_list = tasks.split('\n\n')
           #del tasks_list[-1]
           #del tasks_list[0]
            for task in tasks_list:
                if ('адачи' in task) or ('адача' in task):
                    pass
                else:
                    cursor.execute('INSERT INTO daily_tasks (date, status, task) VALUES (%s, %s, %s)', [datetime.now().date(), 'Новая', task])
                    db.commit()
                    print(task)

        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                print(e)
    except: pass
