import logging as std_logging
from config import Config
from kik import KikApi

std_logging.basicConfig()

logging = std_logging.getLogger('app')


def get_kik_api():
    return KikApi(Config.BOT_USERNAME, Config.BOT_API_KEY)
