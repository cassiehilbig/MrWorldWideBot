from config import Config
from kik import KikApi


def get_kik_api():
    return KikApi(Config.BOT_USERNAME, Config.BOT_API_KEY)
