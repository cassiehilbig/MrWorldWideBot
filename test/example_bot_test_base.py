from bot_test_base import BotTestBase
from secrets import BOT_API_KEY


class BotsworthTestBase(BotTestBase):
    @classmethod
    def setUpClass(cls):
        super(BotsworthTestBase, cls).setUpClass()
        cls.send_messages_location = 'api.default.bot_handler.send_messages'
        cls.api_route = '/receive'
        cls.bot_api_key = BOT_API_KEY
