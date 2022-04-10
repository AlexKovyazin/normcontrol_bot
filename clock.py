from apscheduler.schedulers.blocking import BlockingScheduler
from config import pg_connect, logger


connection, cursor = pg_connect()
schedule = BlockingScheduler()


@schedule.scheduled_job('cron', hour=22)
def reset_msg_counter():
    cursor.execute(f'UPDATE users SET message_count = 0')
    connection.commit()
    logger.info(f'Messages counts was cleaned by reset_msg_counter()')


schedule.start()
