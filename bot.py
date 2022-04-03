import telebot


TOKEN = '2108392950:AAHNePPNGmIbDuLuGPTUHuJKBdFDeWXZfdQ'
SHOW_STAT_COMMAND = 'НОРМОКОНТРОЛЬ, ЁБАНА, НУЖНА СТАТИСТИКА'

bot = telebot.TeleBot(TOKEN)

# Глобальный счетчик сообщений
counter = {}


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


# Run
bot.infinity_polling(timeout=10, long_polling_timeout=5)
