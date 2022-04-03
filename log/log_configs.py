import logging.handlers
import os
import sys


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'logs', 'bot.log')

filename = os.getcwd() + r'\logs\bot_log.txt'

formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

# handler = logging.handlers.TimedRotatingFileHandler(PATH, when='midnight', interval=1, encoding='utf-8')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
