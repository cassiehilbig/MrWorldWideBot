import mock

from test.botsworth_test_base import BotsworthTestBase
from const import MessageType
from lib.admin_requests_mixin import UpdateDisplayNameError
from lib.states.menu.menu_state import MenuStateStrings
from lib.states.update_display_name.update_display_name_flow import UpdateDisplayNameStateStrings
from lib.states.state_types import StateTypes
from model import BotUser


class SelectBotUpdateDisplayNameStateTest(BotsworthTestBase):
    def test_start_flow(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'update display name?'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.UPDATE_DISPLAY_NAME,
            'suggestedResponses': ['abotid', 'Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states,
                         [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT])

    def test_flow_started_answer_with_good_bot_name(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'abotid'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.SELECTED_BOT_NAME.format('abotid'),
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'], 'abotid')
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT), {})
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT])

    def test_flow_started_answer_with_cancel(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'cancel'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU])

    def test_update_display_name_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Superman'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_MESSAGE.format('abotid', 'Superman'),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'], 'abotid')
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'], 'Superman')
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT), {})
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM])

    def test_update_display_name_message_emoji(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': unicode('Superman \U0001f38')}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_MESSAGE.format(
                'abotid', unicode('Superman \U0001f38')
            ),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'], 'abotid')
        self.assertEqual(
            user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'],
            unicode('Superman \U0001f38')
        )
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT), {})
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM])

    def test_update_invalid_display_name_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {
            'from': 'aleem',
            'type': MessageType.TEXT,
            'body': 'Only the best display name in the world'
        }
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_BAD_INPUT,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT])

    def test_update_display_name_picture_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {
            'from': 'aleem',
            'type': MessageType.PICTURE,
            'picUrl': 'http://www.example.com/image.png'
        }
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_INVALID_MESSAGE_TYPE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT])

    def test_update_display_name_cancel_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Cancel'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU])

    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._update_bot_display_name')
    def test_update_display_name_positive_confirmation_message(self, update_display_name):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = 'Superman'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Yeah'}
        outgoing_message_display_name = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_UPDATE_SUCCESS.format('abotid', 'Superman')
        }
        outgoing_message_menu = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message_display_name, outgoing_message_menu])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU])
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM), {})

    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._update_bot_display_name')
    def test_update_display_name_positive_confirmation_message_emoji(self, update_display_name):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = unicode('Superman \U0001f38')
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Yeah'}
        outgoing_message_display_name = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_UPDATE_SUCCESS.format(
                'abotid', unicode('Superman \U0001f38')
            )
        }
        outgoing_message_menu = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message_display_name, outgoing_message_menu])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU])
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM), {})

    def test_update_display_name_negative_confirmation_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = 'Superman'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'No'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_REPLACEMENT_MESSAGE.format('abotid'),
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT])
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM), {})
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT), {'bot-username': 'abotid'})

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._update_bot_display_name',
        side_effect=UpdateDisplayNameError
    )
    def test_update_display_name_confirmation_error(self, update_display_name):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = 'Superman'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Yea'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_UPDATE_ERROR,
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM])

    def test_update_display_name_confirmation_unknown_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = 'Superman'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Potato'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_UNKNOWN_MESSAGE.format(
                'abotid', 'Superman'
            ),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM])

    def test_update_display_name_confirmation_unknown_message_unicode(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM)['display-name'] = unicode('Superman \U0001f38')
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Potato'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_UNKNOWN_MESSAGE.format(
                'abotid', unicode('Superman \U0001f38')
            ),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM])
