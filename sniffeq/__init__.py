import logging
from mongoengine import connect
from sniffeq.settings import DB_NAME, DB_HOST, DB_PORT


# define logging level and format
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s[%(lineno)s]: %(message)s')

# connect to mongoDB
connect(db=DB_NAME, host=DB_HOST, port=DB_PORT)
