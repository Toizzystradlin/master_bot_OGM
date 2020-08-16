import mysql.connector
import json
query_photo_path = 'C:/Users/User/Desktop/projects/DjangoOGM/main/static/images/query_photos/'

def send_message_4(id_employee, query_id):  # функция для отправки уведомления сотруднику
    import telebot
    bot_3 = telebot.TeleBot('1048673690:AAHPT1BfgqOoQ1bBXT1dcSiClLzwwOq0sPU')
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
          "queries.reason, queries.msg FROM " \
          "equipment JOIN queries ON ((queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)) "
    val = (query_id,)
    cursor3.execute(sql, val)
    msg = cursor3.fetchone()
    print(msg)
    try:
        cursor3.execute('SELECT photo_name FROM queries WHERE query_id = %s', [query_id])
        photo = cursor3.fetchone()[0]
        bot_3.send_photo(id_employee, open(query_photo_path + photo, 'rb'))
    except: pass
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_start_now = telebot.types.InlineKeyboardButton('Принимаю', callback_data='start_now')
    keyboard.add(key_start_now)

    bot_3.send_message(id_employee, "У вас новая заявка" + "\n" + "*id_заявки: *" + str(query_id) + "\n" +
                       "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                       "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[3] + "\n" +
                       "*Причина поломки: *" + msg[4] + "\n" + "*Сообщение: *" + str(msg[5]), reply_markup=keyboard,
                       parse_mode="Markdown")

    cursor3.close()

