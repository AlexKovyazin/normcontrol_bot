import os
import telebot
from datetime import datetime, timedelta
from flask import Flask, request
from config import TOKEN, URL
from config import pg_connect, logger


SHOW_STAT_COMMAND = 'НОРМОКОНТРОЛЬ, ЁБАНА, НУЖНА СТАТИСТИКА'
WARNING_MESSAGE = ' ,ТЫ УВЕРЕН, ЧТО НЕ ПИШЕШЬ СЛИШКОМ МНОГО?'
PRE_MUTE_MESSAGE = ' ,ЕЩЁ 5 СООБЩЕНИЙ И ТЫ НЕ СМОЖЕШЬ ПИСАТЬ 24 ЧАСА'
MUTE_MESSAGE = 'ТЫ БЫЛ ПРЕДУПРЕЖДЁН'
MAIN_CHAT_ID = -556566361

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
connection, cursor = pg_connect()


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
    return "!", 200


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    """
    Process message with Flask
    :return: response
    """
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


def mute_user(chat_id, user_id):
    until_date = datetime.now() + timedelta(days=1)
    bot.restrict_chat_member(chat_id, user_id, until_date=until_date)
    logger.debug(f'User with id {user_id} was muted')


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'],
                     func=lambda message: message.text != SHOW_STAT_COMMAND)
def count_messages(message):
    """
    Collect message info, insert/update DB data
    :param message: User's sent message
    :return: None
    """
    print('test')
    sender_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id
    logger.debug(f"User's data was received")

    cursor.execute(
        """SELECT * 
             FROM users 
            WHERE telegram_id = %s 
              AND chat_id = %s""", (sender_id, chat_id)
    )
    user = cursor.fetchone()

    if not user:
        message_count = 1
        cursor.execute(
            """INSERT INTO users (telegram_id, username, firstname, 
                                  lastname, message_count, chat_id) 
                    VALUES (%s, %s, %s, 
                            %s, %s, %s)""", (sender_id, username, first_name,
                                             last_name, message_count, chat_id,)
        )
        connection.commit()
        logger.debug(f'User with id {sender_id} was added to DB')
    else:
        cursor.execute(
            """UPDATE users 
                  SET message_count = message_count + 1 
                WHERE telegram_id = %s 
                  AND chat_id = %s""", (sender_id, chat_id,)
        )
        connection.commit()
        logger.debug(f'Message counter for user with id {sender_id} was updated')

        # Message count checking
        cursor.execute("""SELECT message_count 
                            FROM users 
                           WHERE telegram_id = %s
                             AND chat_id = %s""", (sender_id, chat_id,)
                       )
        users_msg_count = cursor.fetchone()[0]

        if not username:
            username = 'ХЭЙ'
        if users_msg_count == 15:
            warning_message = username + WARNING_MESSAGE
            bot.send_message(message.chat.id, warning_message)
            logger.debug(f'User with id {sender_id} received warning message')
        if users_msg_count == 20:
            pre_warning_message = username + PRE_MUTE_MESSAGE
            bot.send_message(message.chat.id, pre_warning_message)
            logger.debug(f'User with with id {sender_id} received pre mute message')
        if users_msg_count == 25:
            bot.send_message(message.chat.id, MUTE_MESSAGE)
            mute_user(message.chat.id, message.from_user)
            logger.debug(f'User with with id {sender_id} was muted')


@bot.message_handler(func=lambda message: message.text == SHOW_STAT_COMMAND)
def show_stat(message):
    """
    Send message with top 5 users with the highest message counter values
    :param message: SHOW_STAT_COMMAND
    :return: None
    """
    # connection, cursor = pg_connect()

    users_stat = {}
    message_list = []

    cursor.execute("""SELECT * 
                        FROM users 
                       WHERE chat_id = %s 
                    ORDER BY message_count 
                        DESC LIMIT 5""", (MAIN_CHAT_ID,)
                   )
    users_data = cursor.fetchall()
    for user in users_data:
        user_id = user[1]
        username = user[2]
        firstname = user[3]
        lastname = user[4]
        message_count = user[5]
        users_stat[f'{user_id} | {username} | {firstname} {lastname}'] = message_count

    # Prepare list of strings which will be used for message body forming
    for key, value in users_stat.items():
        message_list.append(f'{key}: {value}\n')

    # Making and send message
    stat = ''.join(message_list)
    bot.send_message(message.chat.id, stat)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
