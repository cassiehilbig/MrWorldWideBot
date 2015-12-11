from bot_test_base import BotTestBase
from config import Config


class ExampleBotTestBase(BotTestBase):
    @classmethod
    def setUpClass(cls):
        super(ExampleBotTestBase, cls).setUpClass()
        cls.send_messages_location = 'api.default.bot_handler.send_messages'
        cls.api_route = '/receive'
        cls.bot_api_key = Config.BOT_API_KEY
