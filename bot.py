import os
import telebot
from flask import Flask, request
from config import TOKEN, URL


SHOW_STAT_COMMAND = 'НОРМОКОНТРОЛЬ, ЁБАНА, НУЖНА СТАТИСТИКА'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Глобальный счетчик сообщений
counter = {}


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


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'],
                     func=lambda message: message.text != SHOW_STAT_COMMAND)
def count_messages(message):
    global counter
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if not last_name:
        user_key = first_name
    else:
        user_key = f'{first_name} ' + f'{last_name}'

    if counter.get(user_key):
        counter[user_key] += 1
    else:
        counter[user_key] = 1


@bot.message_handler(func=lambda message: message.text == SHOW_STAT_COMMAND)
def show_stat(message):
    global counter
    message_list = []
    sorted_counter = {}
    sorted_counter_keys = sorted(counter, key=counter.get, reverse=True)

    # Сортируем пользователей в словаре по количеству отправленных сообщений
    for key in sorted_counter_keys:
        sorted_counter[key] = counter[key]

    # Готовим список строк, который будет использоваться формирования сообщения
    for username, message_count in sorted_counter.items():
        message_list.append(f'{username} - {message_count}\n')

    # Формируем сообщение
    stat = ''.join(message_list)

    bot.send_message(message.chat.id, stat)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
