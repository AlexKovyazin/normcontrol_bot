import psycopg2
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from config import DATABASE, USER, PASSWORD, HOST, PORT


connection = psycopg2.connect(
    dbname=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
)
cursor = connection.cursor()
logger = logging.getLogger('bot')
sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=17)
def reset_msg_counter():
    cursor.execute(f'UPDATE users SET message_count = 0')
    connection.commit()
    logger.info(f'Messages counts was cleaned by reset_msg_counter()')


sched.start()
