import os
import telebot
import psycopg2
from flask import Flask, request
from config import TOKEN, URL, DATABASE, USER, PASSWORD, HOST, PORT
from flask_apscheduler import APScheduler
from log.log_configs import logger

SHOW_STAT_COMMAND = 'НОРМОКОНТРОЛЬ, ЁБАНА, НУЖНА СТАТИСТИКА'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
connection = psycopg2.connect(
    dbname=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
)
cursor = connection.cursor()
scheduler = APScheduler()


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
    return "!", 200


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'],
                     func=lambda message: message.text != SHOW_STAT_COMMAND)
def count_messages(message):
    sender_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id

    cursor.execute(
        'SELECT * FROM users WHERE telegram_id=:sender_id AND chat_id=:chat_id',
        {
            'sender_id': sender_id,
            'chat_id': chat_id
        })
    user = cursor.fetchone()

    if not user:
        message_count = 1
        cursor.execute(
            'INSERT INTO users (telegram_id, username, firstname, lastname, message_count, chat_id) '
            'VALUES(:sender_id, :username, :first_name, :last_name, :message_count, :chat_id)',
            {
                'sender_id': sender_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'message_count': message_count,
                'chat_id': chat_id
            })
        connection.commit()
        logger.debug(f'User with telegram id {sender_id} was added to DB')
    else:
        cursor.execute(
            'UPDATE users SET message_count = message_count + 1 '
            'WHERE telegram_id = :sender_id AND chat_id=:chat_id',
            {
                'sender_id': sender_id,
                'chat_id': chat_id
            })
        connection.commit()
        logger.debug(f'Message counter for user with telegram id {sender_id} was updated')


def reset_msg_counter():
    cursor.execute(f'UPDATE users SET message_count = 0')
    connection.commit()
    logger.info(f'Message counts was cleaned by reset_msg_counter()')


@bot.message_handler(func=lambda message: message.text == SHOW_STAT_COMMAND)
def show_stat(message):
    users_stat = {}
    message_list = []

    cursor.execute('SELECT * FROM users ORDER BY message_count DESC LIMIT 5')
    users_data = cursor.fetchall()
    for user in users_data:
        username = user[2]
        firstname = user[3]
        lastname = user[4]
        message_count = user[5]
        users_stat[f'{username}-{firstname} {lastname}'] = message_count

    # Готовим список строк, который будет использоваться формирования сообщения
    for key, value in users_stat.items():
        message_list.append(f'{key}: {value}\n')

    # Формируем и отправляем сообщение
    stat = ''.join(message_list)
    bot.send_message(message.chat.id, stat)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    scheduler.add_job(id='data_r_mess_new', func=reset_msg_counter, trigger='cron', hour=19, minute=0, second=0)
    scheduler.start()
    logger.debug(f'Thread was started')
