from bot_test_base import BotTestBase
from secrets import BOTSWORTH_API_KEY


class BotsworthTestBase(BotTestBase):
    @classmethod
    def setUpClass(cls):
        super(BotsworthTestBase, cls).setUpClass()
        cls.send_messages_location = 'api.default.bot_handler.IncomingMessageTask._send_messages'
        cls.api_route = '/message'
        cls.bot_api_key = BOTSWORTH_API_KEY
