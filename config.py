import psycopg2
import logging
import sys


TOKEN = '2108392950:AAHNePPNGmIbDuLuGPTUHuJKBdFDeWXZfdQ'
URL = 'https://normcontrolbot.herokuapp.com/'

# Database
HOST = 'ec2-63-35-156-160.eu-west-1.compute.amazonaws.com'
DATABASE = 'd6m2902kvhirdq'
USER = 'uhsyrrueybiiph'
PORT = 5432
PASSWORD = '501052069e716f618e439df4e8c27319f347e8dc00dd10e0c2da901c2d2976e1'
URI = 'postgres://uhsyrrueybiiph:501052069e716f618e439df4e8c27319f347e8dc00dd10e0c2da901c2d2976e1@ec2-63-35-156-160.eu-west-1.compute.amazonaws.com:5432/d6m2902kvhirdq'

formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def pg_connect():
    connection = psycopg2.connect(
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
    )
    cursor = connection.cursor()
    return connection, cursor
